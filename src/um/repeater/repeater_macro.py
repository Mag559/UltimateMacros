from enum import Enum

import re
from logging import getLogger
from threading import Thread
from pathlib import Path
from time import sleep

from um.base_macro import BaseMacro, ImportantEvents
from um.profiles import ProfileReader
from .interpreter import Interpreter
from .recorder import Recorder

MACRO_FILES = Path(__file__).parents[3] / "macro_files"


class RepeaterMacro(BaseMacro):
    """
    Macro mix of recorder and interpreter
    TOGGLE to pause recording or executing instructions
    SHORTCUT1 to start recording or end recording
    SHORTCUT2 to start execution of last instruction set or end it prematurely

    Pressing SHORTCUT2 while recording ends it
    """
    class State(Enum):
        IDLE = 0
        RECORDING = 1
        INTERPRETING = 3


    def __init__(self, dir_path: Path | None = None):
        super().__init__()
        self.repeater_logger = getLogger(__name__)

        self._recorder: Recorder | None = None
        self._record_thread: Thread | None = None

        self._interpreter: Interpreter | None = None
        self._interpreter_thread: Thread | None = None

        if dir_path is None:
            self._dir_path: Path = MACRO_FILES / "repeater"
        else:
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


    def start(self):
        self.repeater_logger.debug("Repeater starting")
        super().start()

        if self._interpreter_thread is not None:
            self._interpreter_thread.join()
        if self._record_thread is not None:
            self._record_thread.join()

        self.repeater_logger.debug("Repeater start method ended")


    def _update(self, event_code: ImportantEvents):
        super()._update(event_code)

        if self._stop_flag:
            return

        match event_code:
            case ImportantEvents.TOGGLE:
                self._pause_toggle = True

            case ImportantEvents.SHORTCUT1:
                if self.state == RepeaterMacro.State.RECORDING:
                    self.stop_recording()
                elif self.state == RepeaterMacro.State.IDLE:
                    self.start_recording()

            case ImportantEvents.SHORTCUT2:
                if self.state == RepeaterMacro.State.INTERPRETING:
                    self.stop_interpreting()
                elif self.state == RepeaterMacro.State.IDLE:
                    self.start_interpreting()


    def start_recording(self):
        self._file_idx += 1
        self.state = RepeaterMacro.State.RECORDING

        self.repeater_logger.debug("Repeater recording started")
        self._recorder = Recorder()
        self._record_thread = Thread(target=self._record, name="RepeaterMacro record")

        self._record_thread.start()


    def stop_recording(self):
        if self._recorder is None:
            return
        self._recorder.stop()
        self._record_thread.join()

        self.repeater_logger.debug("Repeater recording ended")

        self.state = RepeaterMacro.State.IDLE


    def start_interpreting(self):
        self.state = RepeaterMacro.State.INTERPRETING

        self.repeater_logger.debug(f"Interpreting started")

        self._interpreter = Interpreter(self._read_instructions())
        self._interpreter_thread = Thread(target=self._interpreter.start, name="RepeaterMacro interpreter")

        self._interpreter_thread.start()


    def stop_interpreting(self):
        self._end_interpreting_flag = True

        if self._interpreter_thread is None:
            return

        self._interpreter_thread.join()

        self.repeater_logger.debug(f"Interpreting ended")


    def stop(self):
        self.repeater_logger.debug(f"Raising stop flag")
        self._stop_flag = True
        self._pause = False

        self.stop_recording()
        super().stop()

    def _get_current_file(self):
        return self._dir_path / f"{self._file_idx}.ins"


    def _record(self):
        with open(self._get_current_file(), 'w') as file:
            for instruction in self._recorder.start():
                # make sure the update function runs first
                # only slows down the consumer thread on the recorder, so inputs should still be timestamped correctly
                sleep(ProfileReader.profile().macro_recorder_record_thread_delay)

                if self._pause or self._pause_toggle:
                    self._pause_mode(instruction, file)
                    continue

                self._write_to_file_mode(instruction, file)

    def _pause_mode(self, instruction: str, file):
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


    def _write_to_file_mode(self, instruction: str, file):
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


    def _read_instructions(self):
        if self._get_current_file().exists():
            with open(self._get_current_file(), "r") as file:
                for line in file:

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
                        return
                    yield line
        else:
            self.repeater_logger.debug(f"File {self._get_current_file()} does not exist")

        self.repeater_logger.debug(f"Read all instructions from {self._get_current_file()}")
        self.state = RepeaterMacro.State.IDLE
