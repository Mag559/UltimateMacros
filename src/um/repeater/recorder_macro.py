import re
from logging import getLogger, Logger
from pathlib import Path
from threading import Thread

import um.base_macro
from .recorder import Recorder
from um.profiles import MACRO_FILES
from um.helper_classes import LoggingThread


class RecorderMacro(um.base_macro.BaseMacro):
    """
    Macro version of the recorder
    Filters out SHORTCUT1 and TOGGLE.
    TOGGLE -> pause recording instructions.
    Inputs are still recorded while paused, but they are written as comments in the file
    3x Alt + ` in quick succession -> exit the macro
    """

    def __init__(self, file_path: Path | str):
        """

        :param file_path: path of a text file to record the instructions to,
        relative to `macro_files` in the project root directory.
        """
        self.recorder_macro_logger: Logger = getLogger(__name__)
        super().__init__(status_window_kwargs={
            "name": "RecorderMacro",
            "state": "initializing"
        })

        self._recorder = Recorder()
        self._file_path = MACRO_FILES / file_path

        self._events_buffer: list = []
        self._possible_shortcut = False

        self._pause: bool = False
        self._pause_toggle: bool = False

        self.recorder_thread: Thread = LoggingThread(
            name="Recorder in macro recorder",
            target=self._record
        )

    def start(self) -> None:
        """
        Start recording instructions.
        :return:
        """
        self.recorder_thread.start()
        self.status_window.set_state("recording")
        super().start()
        self.recorder_thread.join()

    def _update(self, event_code: um.base_macro.ImportantEvent) -> bool:
        """
        Handle Important Events.
        :param event_code: important event to handle (TOGGLE is handled)
        :return: True if the macro was terminated, false otherwise
        """
        if event_code == um.base_macro.ImportantEvent.TOGGLE:
            self._pause_toggle = True

        return super()._update(event_code)

    def _record(self) -> None:
        """
        Write the instructions recorded by the Recorder to the file.
        Due to a very low priority in the OrderedEmitter, should run after all the other handlers.
        :return:
        """
        self.recorder_macro_logger.debug(f"Start recording")
        with open(self._file_path, 'w') as file:
            for instruction in self._recorder.start():
                if self._pause or self._pause_toggle:
                    self.status_window.set_details(f"Commented instruction: {instruction}")
                    self._pause_mode(instruction, file)
                    continue

                self.status_window.set_details(f"Recorded instruction: {instruction}")
                self._write_to_file_mode(instruction, file)
        self.recorder_macro_logger.debug(f"Ended recording")

    def _pause_mode(self, instruction: str, file) -> None:
        """
        Process instruction in pause mode:
        still write it to the file but only in the form of extracted key / button abd as a comment.
        Also detect TOGGLE and SHORTCUT1 to be filtered out.
        :param instruction: instruction recorded by the Recorder
        :param file: opened file
        :return:
        """
        self.logger.debug(f"Processing instruction: {instruction} in pause mode")

        if not self._pause and self._pause_toggle:
            file.write("---")

        if instruction.find("num_lock") == -1 and instruction.find("release") != -1:
            file.write(instruction.rsplit(" ", 1)[1] + " ")

        if self._pause and self._pause_toggle:
            file.write("---\n")

        if self._pause_toggle:
            self._pause_toggle = False
            self._pause = not self._pause
            self.status_window.set_state("paused" if self._pause else "recording")

    def _write_to_file_mode(self, instruction: str, file) -> None:
        """
        Check if the instruction isn't the TOGGLE or SHORTCUT1 to be filtered out.
        Deffer the decision by using a buffer if needed.
        If it passes as a 'regular' instruction, it is written to the file.
        :param instruction: considered instruction recorded by the Recorder
        :param file: opened file
        :return:
        """
        self.logger.debug(f"Processing instruction: {instruction} in write mode")

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

    def stop(self):
        """
        Stop recording instructions and the macro.
        :return:
        """
        self._recorder.stop()
        super().stop()
