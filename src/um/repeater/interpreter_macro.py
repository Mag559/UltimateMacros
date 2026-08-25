from logging import getLogger
from pathlib import Path
from threading import Thread
from time import sleep

import um.base_macro
from um.profiles import ProfileReader, MACRO_FILES
from .interpreter import Interpreter
from um.helper_classes import LoggingThread


class InterpreterMacro(um.base_macro.BaseMacro):
    """
    Macro version of the Interpreter.
    TOGGLE -> pause execution (after executing the current instruction is done, not immediately)
    3x Alt + ` in quick succession -> exit the macro
    """

    def __init__(self, file_path: Path | str):
        """

        :param file_path: path to the text file with instructions, relative to `macro_files`,
        by convention with .ins extension
        """
        super().__init__()
        self.int_logger = getLogger(__name__)
        self._file_path = MACRO_FILES / file_path

        self._pause: bool = False
        # could do it with the threading library and pass the interpreter an event to wait on
        # for use cases where the sleep times are longer
        self._stop_flag: bool = False

        with open(self._file_path, "r") as file:
            file_instructions: list[str] = file.readlines()

        self.interpreter: Interpreter = Interpreter(
            file_instructions,
            before_next_instruction_callback=self._should_keep_going
        )
        self.interpreter_thread: Thread = LoggingThread(
            name="Interpreter in macro interpreter",
            target=self._interpret
        )

    def _update(self, event_code: um.base_macro.ImportantEvent) -> bool:
        """
        Handle important events
        :param event_code: ImportantEvent to handle (TOGGLE is handled)
        :return: True if the macro was terminated, false otherwise
        """
        if event_code == um.base_macro.ImportantEvent.TOGGLE:
            self._pause = not self._pause

        return super()._update(event_code)

    def start(self) -> None:
        """
        Start the Interpreter Macro
        :return:
        """
        self.interpreter_thread.start()
        super().start()

    def _should_keep_going(self) -> bool:
        """
        Method called by the Interpreter object.
        Halts execution or ends it when appropriate
        :return: True if the instruction execution should proceed, False if it should stop
        """
        while self._pause:
            sleep(ProfileReader.profile().macro_interpreter_sleep_spf)

        if self._stop_flag:
            self.int_logger.debug(f"Stopped reading instructions from {self._file_path}")
            return False
        return True

    def _interpret(self) -> None:
        """
        Method run from a thread for interpreting,
        stops the macro, if the interpreter naturally runs out of instructions
        """
        self.int_logger.debug(f"Interpreting started")
        self.interpreter.start()
        if not self._stop_flag:
            self.stop()
        self.int_logger.debug(f"Interpreting ended")

    def stop(self) -> None:
        """
        End the macro execution.
        :return:
        """
        self.int_logger.debug(f"Raising stop flag")
        self._stop_flag = True
        self._pause = False
        self.interpreter_thread.join()
        super().stop()
