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

        self.recorder: Recorder | None = None
        self.record_thread: Thread | None = None

        self.interpreter: Interpreter | None = None
        self.interpreter_thread: Thread | None = None

        if dir_path is None:
            self.dir_path: Path = MACRO_FILES / "repeater"
        else:
            self.dir_path: Path = dir_path

        # probably unneeded safeguards
        if not self.dir_path.is_dir():
            self.dir_path.unlink(missing_ok=True)

        self.dir_path.mkdir(parents=True, exist_ok=True)

        self.file_idx: int = -1

        self.events_buffer: list = []
        self.possible_shortcut = False

        self.state: RepeaterMacro.State = RepeaterMacro.State.IDLE
        self.pause: bool = False
        self.pause_toggle: bool = False

        self.stop_flag: bool = False

        self.end_interpreting_flag: bool = False

    def start(self):
        self.repeater_logger.debug("Repeater starting")
        super().start()

        if self.interpreter_thread is not None:
            self.interpreter_thread.join()
        if self.record_thread is not None:
            self.record_thread.join()

        self.repeater_logger.debug("Repeater start method ended")

    def update(self, event_code: ImportantEvents):
        super().update(event_code)

        if self.stop_flag:
            return

        match event_code:
            case ImportantEvents.TOGGLE:
                self.pause_toggle = True

            case ImportantEvents.SHORTCUT1:
                pass
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
        self.file_idx += 1
        self.state = RepeaterMacro.State.RECORDING

        self.repeater_logger.debug("Repeater recording started")
        self.recorder = Recorder()
        self.record_thread = Thread(target=self.record, name="RepeaterMacro record")

        self.record_thread.start()

    def stop_recording(self):
        if self.recorder is None:
            return
        self.recorder.stop()
        self.record_thread.join()

        self.repeater_logger.debug("Repeater recording ended")

        self.state = RepeaterMacro.State.IDLE

    def start_interpreting(self):
        self.state = RepeaterMacro.State.INTERPRETING

        self.repeater_logger.debug(f"Interpreting started")

        self.interpreter = Interpreter(self.read_instructions())
        self.interpreter_thread = Thread(target=self.interpreter.start, name="RepeaterMacro interpreter")

        self.interpreter_thread.start()

    def stop_interpreting(self):
        self.end_interpreting_flag = True

        if self.interpreter_thread is None:
            return

        self.interpreter_thread.join()

        self.repeater_logger.debug(f"Interpreting ended")

    def terminate(self):
        self.repeater_logger.debug(f"Raising stop flag")
        self.stop_flag = True
        self.pause = False

        self.stop_recording()
        super().terminate()

    def get_current_file(self):
        return self.dir_path / f"{self.file_idx}.ins"

    def record(self):
        with open(self.get_current_file(), 'w') as file:
            for instruction in self.recorder.start():
                # make sure the update function runs first
                # only slows down the consumer thread on the recorder, so inputs should still be timestamped correctly
                sleep(ProfileReader.profile().macro_recorder_record_thread_delay)

                if self.pause or self.pause_toggle:
                    self.pause_mode(instruction, file)
                    continue

                self.write_to_file_mode(instruction, file)

    def pause_mode(self, instruction: str, file):
        self.repeater_logger.debug(f"Processing instruction: {instruction} in pause mode")

        if not self.pause and self.pause_toggle:
            file.write("---")

        if instruction.find("num_lock") == -1 and instruction.find("release") != -1:
            file.write(instruction.rsplit(" ", 1)[1])

        if self.pause and self.pause_toggle:
            file.write("---\n")

        if self.pause_toggle:
            self.pause_toggle = False
            self.pause = not self.pause

    def write_to_file_mode(self, instruction: str, file):
        self.repeater_logger.debug(f"Processing instruction: {instruction} in write mode")

        if re.search(r"num_lock", instruction):
            return

        # if ` is pressed next it's a shortcut, so have to start buffering
        if re.search(r"press alt_l", instruction):
            self.possible_shortcut = True
            self.events_buffer.append(instruction)
            return

        # no possible shortcut rn
        if not self.possible_shortcut:
            file.write(instruction + "\n")
            return

        # it was a shortcut, cut it out
        if re.search(r"release alt_l", instruction) and len(self.events_buffer) > 0:
            self.possible_shortcut = False
            self.events_buffer.clear()
            return

        self.events_buffer.append(instruction)

        # not the shortcut after all, write the buffered inputs into the file
        if not re.search(r"`", instruction):
            self.possible_shortcut = False
            for event in self.events_buffer:
                file.write(event + "\n")
            self.events_buffer.clear()

    def read_instructions(self):
        if self.get_current_file().exists():
            with open(self.get_current_file(), "r") as file:
                for line in file:

                    if self.pause_toggle:
                        self.pause = True
                        self.pause_toggle = False

                    while self.pause:
                        sleep(ProfileReader.profile().macro_interpreter_sleep_spf)
                        if self.pause_toggle:
                            self.pause = False
                            self.pause_toggle = False

                    if self.stop_flag or self.end_interpreting_flag:
                        self.repeater_logger.debug(f"Stopped reading instructions from {self.get_current_file()}")
                        self.end_interpreting_flag = False
                        return
                    yield line
        else:
            self.repeater_logger.debug(f"File {self.get_current_file()} does not exist")

        self.repeater_logger.debug(f"Read all instructions from {self.get_current_file()}")
        self.state = RepeaterMacro.State.IDLE
