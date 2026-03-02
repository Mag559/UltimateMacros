from enum import Enum

from base_macro import BaseMacro
import re
from threading import Thread
from pathlib import Path
from time import sleep

from base_macro import BaseMacro, ImportantEvents
from .interpreter import Interpreter
from .recorder import Recorder

class RepeaterState(Enum):
    IDLE = 0
    RECORDING = 1
    EXECUTING = 3

# TODO does not work yet
class RepeaterMacro(BaseMacro):
    """
    Macro mix of recorder and interpreter
    TOGGLE to pause recording or executing instructions
    SHORTCUT1 to start recording or end recording
    SHORTCUT2 to start execution of last instruction set or end it prematurely

    Pressing SHORTCUT2 while recording ends it
    """

    def __init__(self, file_path: Path | None = None):
        super().__init__()

        self.recorder = Recorder()
        self.record_thread = Thread(target=self.record, name="RepeaterMacro record")

        self.interpreter: Interpreter = Interpreter(self.read_instructions())
        self.interpreter_thread: Thread = Thread(target=self.interpreter.start, name="RepeaterMacro interpreter")

        self.file_path: Path | None = file_path

        self.events_buffer: list = []
        self.possible_shortcut = False

        self.state: RepeaterState = RepeaterState.IDLE
        self.pause: bool = False
        self.pause_toggle: bool = False

        self.stop_flag: bool = False


    def update(self, event_code: ImportantEvents):
        super().update(event_code)

        if event_code == ImportantEvents.TOGGLE:
            self.pause_toggle = True


    def record(self):
        with open(self.file_path, 'w') as file:
            for instruction in self.recorder.start():
                # make sure the update function runs first
                # only slows down the consumer thread on the recorder, so inputs should still be timestamped correctly
                sleep(0.1)

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

    def terminate(self):
        self.recorder.stop()
        super().terminate()




def update(self, event_code: ImportantEvents):
    super().update(event_code)

    if event_code == ImportantEvents.TOGGLE:
        self.pause = not self.pause


def start(self):
    self.int_logger.debug(f"Interpreting started")
    self.interpreter_thread.start()
    super().start()
    self.interpreter_thread.join()
    self.int_logger.debug(f"Interpreting ended")


def read_instructions(self):
    with open(self.file_path, "r") as file:
        for line in file:

            while self.pause:
                sleep(0.1)

            if self.stop_flag:
                self.int_logger.debug(f"Stopped reading instructions from {self.file_path}")
                return
            yield line

    self.int_logger.debug(f"Read all instructions from {self.file_path}")

    self.terminate()


def terminate(self):
    self.int_logger.debug(f"Raising stop flag")
    self.stop_flag = True
    self.pause = False
    super().terminate()
