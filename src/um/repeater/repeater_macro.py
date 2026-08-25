import re
from enum import Enum
from logging import getLogger
from pathlib import Path
from threading import Thread
from time import sleep

import um.base_macro
from um.profiles import ProfileReader, MACRO_FILES
from .interpreter import Interpreter
from .recorder import Recorder
from um.helper_classes.logging_thread import LoggingThread


class RepeaterMacro(um.base_macro.BaseMacro):
    """
    Macro mix of recorder and interpreter
    TOGGLE -> pause recording or executing instructions
    SHORTCUT1 -> start recording or end recording
    SHORTCUT2 -> start execution of latest instruction set or end it prematurely

    Pressing SHORTCUT2 while recording or SHORTCUT1 while interpreting (unless 3x to terminate) does nothing
    """

    class State(Enum):
        IDLE = 0
        RECORDING = 1
        INTERPRETING = 3

    def __init__(self, dir_path: Path = MACRO_FILES / "repeater"):
        """

        :param dir_path: path of the directory to store recorded scripts,
        absolute or relative to project root if program is run in the right way
        """
        super().__init__()
        self.repeater_logger = getLogger(__name__)

        self._recorder: Recorder | None = None
        self._record_thread: Thread | None = None

        self._interpreter: Interpreter | None = None
        self._interpreter_thread: Thread | None = None

        self._dir_path: Path = dir_path

        # probably unneeded safeguards
        if not self._dir_path.is_dir():
            self._dir_path.unlink(missing_ok=True)

        self._dir_path.mkdir(parents=True, exist_ok=True)

        self._file_idx: int = -1

        self._events_buffer: list = []
        self._possible_shortcut = False

        self.state: RepeaterMacro.State = RepeaterMacro.State.IDLE
        self._pause: bool = False
        self._pause_toggle: bool = False

        self._stop_flag: bool = False

        self._end_interpreting_flag: bool = False

    def start(self) -> None:
        """
        Start the macro. Don't start either the Recorder or the Interpreter yet, wait for the user.
        :return:
        """
        self.repeater_logger.debug("Repeater starting")
        super().start()

        if self._interpreter_thread is not None:
            self._interpreter_thread.join()
        if self._record_thread is not None:
            self._record_thread.join()

        self.repeater_logger.debug("Repeater start method ended")

    def _update(self, event_code: um.base_macro.ImportantEvent) -> bool:
        """
        Handle the Important Event.
        :param event_code: Important Event to handle (TOGGLE, SHORTCUT1 and SHORTCUT2 are handled)
        :return: True if the macro was terminated, false otherwise
        """
        was_terminated: bool = super()._update(event_code)

        if self._stop_flag or was_terminated:
            return True

        match event_code:
            case um.base_macro.ImportantEvent.TOGGLE:
                self._pause_toggle = True

            case um.base_macro.ImportantEvent.SHORTCUT1:
                if self.state == RepeaterMacro.State.RECORDING:
                    self.stop_recording()
                elif self.state == RepeaterMacro.State.IDLE:
                    self.start_recording()

            case um.base_macro.ImportantEvent.SHORTCUT2:
                if self.state == RepeaterMacro.State.INTERPRETING:
                    self.stop_interpreting()
                elif self.state == RepeaterMacro.State.IDLE:
                    self.start_interpreting()

        return False

    def start_recording(self) -> None:
        """
        Asynchronously start recording user inputs with a Recorder
        :return:
        """
        self._file_idx += 1
        self.state = RepeaterMacro.State.RECORDING

        self.repeater_logger.debug("Repeater recording started")
        self._recorder = Recorder()
        self._record_thread = LoggingThread(target=self._record, name="RepeaterMacro record")

        self._record_thread.start()

    def stop_recording(self) -> None:
        """
        Stop recording user inputs.
        :return:
        """
        if self._recorder is None:
            return
        self._recorder.stop()
        self._record_thread.join()

        self.repeater_logger.debug("Repeater recording ended")

        self.state = RepeaterMacro.State.IDLE
        self._recorder = None

    def start_interpreting(self) -> None:
        """
        Asynchronously start interpreting instructions from the latest file:
        `-1.ins` if no recording has been triggered during the lifetime of this macro,
        `0.ins` if one recording has been done .
        The counter resets if macro is terminated and rerun within the same program session.
        :return:
        """
        self.state = RepeaterMacro.State.INTERPRETING

        self.repeater_logger.debug(f"Interpreting started")

        self._interpreter = Interpreter(
            self._read_instructions(),
            before_next_instruction_callback=self._should_keep_going
        )
        self._interpreter_thread = LoggingThread(target=self._interpret, name="RepeaterMacro interpreter")

        self._interpreter_thread.start()

    def _interpret(self) -> None:
        self._interpreter.start()
        self.state = RepeaterMacro.State.IDLE

    def stop_interpreting(self) -> None:
        """
        Terminate the interpreting early.
        Does not get called when interpreting ends naturally - due to no further instructions.
        :return:
        """
        self._end_interpreting_flag = True

        if self._interpreter_thread is None:
            return

        self._interpreter_thread.join()

        self.repeater_logger.debug(f"Interpreting ended")

    def stop(self) -> None:
        """
        Stop the whole macro.
        Interpreting is ended by the ``self._stop_flag`` and recording with ``self.stop_recording()``
        :return:
        """
        self.repeater_logger.debug(f"Raising stop flag")
        self._stop_flag = True
        self._pause = False

        self.stop_recording()
        super().stop()

    def _get_current_file(self) -> Path:
        """
        Get the latest file with instructions in the directory specified in the constructor.
        `-1.ins` if no recording has been triggered during the lifetime of this macro,
        `0.ins` if 1 has been triggered and so on.
        :return:
        """
        return self._dir_path / f"{self._file_idx}.ins"

    def _record(self) -> None:
        """
        Write the instructions recorded by the Recorder to the file.
        Due to a very low priority in the OrderedEmitter, should run after all the other handlers.
        :return:
        """
        with open(self._get_current_file(), 'w') as file:
            for instruction in self._recorder.start():
                if self._pause or self._pause_toggle:
                    self._pause_mode(instruction, file)
                    continue

                self._write_to_file_mode(instruction, file)

    def _pause_mode(self, instruction: str, file) -> None:
        """
        Process instruction in pause mode:
        still write it to the file but only in the form of extracted key / button abd as a comment.
        Also detect TOGGLE and SHORTCUT1 to be filtered out.
        :param instruction: instruction recorded by the Recorder
        :param file: opened file
        :return:
        """
        self.repeater_logger.debug(f"Processing instruction: {instruction} in pause mode")

        if not self._pause and self._pause_toggle:
            file.write("---")

        if instruction.find("num_lock") == -1 and instruction.find("release") != -1:
            file.write(instruction.rsplit(" ", 1)[1])

        if self._pause and self._pause_toggle:
            file.write("---\n")

        if self._pause_toggle:
            self._pause_toggle = False
            self._pause = not self._pause

    def _write_to_file_mode(self, instruction: str, file) -> None:
        """
        Check if the instruction isn't the TOGGLE or SHORTCUT1 to be filtered out.
        Deffer the decision by using a buffer if needed.
        If it passes as a 'regular' instruction, it is written to the file.
        :param instruction: considered instruction recorded by the Recorder
        :param file: opened file
        :return:
        """
        self.repeater_logger.debug(f"Processing instruction: {instruction} in write mode")

        if re.search(r"num_lock", instruction):
            return

        # if ` is pressed next it's a shortcut, so have to start buffering
        if re.search(r"press alt_l", instruction):
            self._possible_shortcut = True
            self._events_buffer.append(instruction)
            return

        # no possible shortcut rn
        if not self._possible_shortcut:
            file.write(instruction + "\n")
            return

        # it was a shortcut, cut it out
        if re.search(r"release alt_l", instruction) and len(self._events_buffer) > 0:
            self._possible_shortcut = False
            self._events_buffer.clear()
            return

        self._events_buffer.append(instruction)

        # not the shortcut after all, write the buffered inputs into the file
        if not re.search(r"`", instruction):
            self._possible_shortcut = False
            for event in self._events_buffer:
                file.write(event + "\n")
            self._events_buffer.clear()

    def _should_keep_going(self) -> bool:
        """
        Method called by the Interpreter object.
        Halts execution or ends it when appropriate
        :return: True if the instruction execution should proceed, False if it should stop
        """

        if self._pause_toggle:
            self._pause = True
            self._pause_toggle = False

        while self._pause:
            sleep(ProfileReader.profile().macro_interpreter_sleep_spf)
            if self._pause_toggle:
                self._pause = False
                self._pause_toggle = False

        if self._stop_flag or self._end_interpreting_flag:
            self.repeater_logger.debug(f"Stopped reading instructions from {self._get_current_file()}")
            self._end_interpreting_flag = False
            return False

        return True

    def _read_instructions(self) -> list[str]:
        """
        Reads the instructions from the file and return them in the form of a generator.
        :return: list of instructions read from the file or empty list if file doesn't exist
        """
        if self._get_current_file().exists():
            with open(self._get_current_file(), "r") as file:
                return file.readlines()
        else:
            self.repeater_logger.debug(f"File {self._get_current_file()} does not exist")
            return []
