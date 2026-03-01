from pathlib import Path
from threading import Thread
from time import sleep
from logging import getLogger

from base_macro import BaseMacro, ImportantEvents
from .interpreter import Interpreter

class InterpreterMacro(BaseMacro):
    """
    Macro version of the recorder
    Filters out SHORTCUT1
    """
    def __init__(self, file_path: Path):
        super().__init__()
        self.int_logger = getLogger(__name__)
        self.file_path = file_path

        self.pause: bool = False
        self.stop_flag: bool = False
        self.interpreter: Interpreter = Interpreter(self.read_instructions())
        self.interpreter_thread: Thread = Thread(target=self.interpreter.start, name="InterpreterMacro interpreter")


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
