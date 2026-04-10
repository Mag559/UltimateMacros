from enum import Enum

import re
from threading import Thread
from pathlib import Path
from time import sleep

from src.base_macro import BaseMacro, ImportantEvents
from src.profiles import ProfileReader
from .interpreter import Interpreter
from .recorder import Recorder


MACRO_FILES = Path(__file__).parents[2] / "macro_files"

class RepeaterState(Enum):
    IDLE = 0
    RECORDING = 1
    INTERPRETING = 3

# TODO does not work yet
class RepeaterMacro(BaseMacro):
    """
    Macro mix of recorder and interpreter
    TOGGLE to pause recording or executing instructions
    SHORTCUT1 to start recording or end recording
    SHORTCUT2 to start execution of last instruction set or end it prematurely

    Pressing SHORTCUT2 while recording ends it
    """

    def __init__(self, dir_path: Path | None = None):
        super().__init__()

        self.recorder: Recorder | None = None
        self.record_thread: Thread | None = None

        self.interpreter: Interpreter = Interpreter(self.read_instructions())
        self.interpreter_thread: Thread = Thread(target=self.interpreter.start, name="RepeaterMacro interpreter")

        if dir_path is None:
            self.dir_path: Path = MACRO_FILES / "repeater"
        else:
            self.dir_path: Path = dir_path

        # probably unneeded safeguards
        if not self.dir_path.is_dir():
            self.dir_path.unlink(missing_ok=True)

        self.dir_path.mkdir(parents=True, exist_ok=True)

        self.file_idx: int = 1

        self.events_buffer: list = []
        self.possible_shortcut = False

        self.state: RepeaterState = RepeaterState.IDLE
        self.pause: bool = False
        self.pause_toggle: bool = False

        self.stop_flag: bool = False

        self.end_interpreting_flag: bool = False


    def start(self):
        self.logger.debug("Repeater starting")
        self.interpreter_thread.start()
        self.logger.debug("Starting interpreter (active the whole time)")
        super().start()

        self.interpreter_thread.join()
        self.record_thread.join()

        self.logger.debug("Repeater start method ended")


    def update(self, event_code: ImportantEvents):
        super().update(event_code)

        match event_code:
            case ImportantEvents.TOGGLE:
                self.pause_toggle = True

            case ImportantEvents.SHORTCUT1:
                if self.state == RepeaterState.RECORDING:
                    self.stop_recording()
                elif self.state == RepeaterState.IDLE:
                    self.start_recording()

            case ImportantEvents.SHORTCUT2:
                if self.state == RepeaterState.INTERPRETING:
                    self.stop_interpreting()
                elif self.state == RepeaterState.IDLE:
                    self.start_interpreting()


    def start_recording(self):
        self.file_idx += 1
        self.logger.debug("Repeater recording started")
        self.recorder = Recorder()
        self.record_thread = Thread(target=self.record, name="RepeaterMacro record")
        self.record_thread.start()
        self.record_thread.join()
        self.logger.debug("Repeater recording ended")


    def stop_recording(self):
        self.recorder.stop()


    def start_interpreting(self):
        self.logger.debug(f"Interpreting started")
        self.interpreter_thread.start()
        self.interpreter_thread.join()
        self.logger.debug(f"Interpreting ended")


    def stop_interpreting(self):
        self.end_interpreting_flag = True


    def terminate(self):
        self.logger.debug(f"Raising stop flag")
        self.recorder.stop()
        self.stop_flag = True
        self.pause = False
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
        self.logger.debug(f"Processing instruction: {instruction} in pause mode")

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
        self.logger.debug(f"Processing instruction: {instruction} in write mode")

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
        with open(self.get_current_file(), "r") as file:
            for line in file:

                while self.pause:
                    sleep(ProfileReader.profile().macro_interpreter_sleep_spf)

                if self.stop_flag or self.end_interpreting_flag:
                    self.logger.debug(f"Stopped reading instructions from {self.get_current_file()}")
                    self.end_interpreting_flag = False
                    return
                yield line

        self.logger.debug(f"Read all instructions from {self.dir_path}")
        self.state = RepeaterState.IDLE
