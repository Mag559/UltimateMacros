import re
from logging import getLogger, Logger
from pathlib import Path


from um.base_macro import BaseMacro, ImportantEvents
from .recorder import Recorder

class RecorderMacro(BaseMacro):
    """
    Macro version of the recorder
    Filters out SHORTCUT1 and TOGGLE.
    TOGGLE - to pause recording instructions,
    instead comments are made in the file
    """
    def __init__(self, file_path: Path):
        self.recorder_macro_logger: Logger = getLogger(__name__)
        super().__init__()

        self._recorder = Recorder()
        self._file_path = file_path

        self._events_buffer: list = []
        self._possible_shortcut = False

        self._pause: bool = False
        self._pause_toggle: bool = False


    def start(self):
        self.recorder_macro_logger.debug(f"Start recording")
        super()._run()
        self._record()
        self.recorder_macro_logger.debug(f"Ended recording")


    def _update(self, event_code: ImportantEvents):
        super()._update(event_code)

        if event_code == ImportantEvents.TOGGLE:
            self._pause_toggle = True


    def _record(self):
        with open(self._file_path, 'w') as file:
            for instruction in self._recorder.start():
                # update should run first due to priorities in the ordered emitter

                if self._pause or self._pause_toggle:
                    self._pause_mode(instruction, file)
                    continue

                self._write_to_file_mode(instruction, file)


    def _pause_mode(self, instruction: str, file):
        self.logger.debug(f"Processing instruction: {instruction} in pause mode")

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
        self._recorder.stop()
        super().stop()
