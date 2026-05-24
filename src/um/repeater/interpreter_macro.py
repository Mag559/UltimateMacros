from pathlib import Path
from time import sleep
from logging import getLogger

from um.profiles import ProfileReader
from um.base_macro import BaseMacro, ImportantEvents
from .interpreter import Interpreter

class InterpreterMacro(BaseMacro):
    """
    Macro version of the interpreter
    TOGGLE to pause execution
    """
    def __init__(self, file_path: Path):
        super().__init__()
        self.int_logger = getLogger(__name__)
        self.file_path = file_path

        self.pause: bool = False
        # could do it with the threading library and pass the interpreter an event to wait on
        # for use cases where the sleep times are longer
        self.stop_flag: bool = False
        self.interpreter: Interpreter = Interpreter(self.read_instructions())


    def _update(self, event_code: ImportantEvents):
        super()._update(event_code)

        if event_code == ImportantEvents.TOGGLE:
            self.pause = not self.pause


    def start(self):
        super()._run()
        self.int_logger.debug(f"Interpreting started")
        self.interpreter.start()
        self.int_logger.debug(f"Interpreting ended")


    def read_instructions(self):
        with open(self.file_path, "r") as file:
            for line in file:

                while self.pause:
                    sleep(ProfileReader.profile().macro_interpreter_sleep_spf)

                if self.stop_flag:
                    self.int_logger.debug(f"Stopped reading instructions from {self.file_path}")
                    return
                yield line

        self.int_logger.debug(f"Read all instructions from {self.file_path}")

        self.stop()


    def stop(self):
        self.int_logger.debug(f"Raising stop flag")
        self.stop_flag = True
        self.pause = False
        super().stop()
