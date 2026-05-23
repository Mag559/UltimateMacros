import re
from threading import Thread
from pathlib import Path
from time import sleep

from um.profiles import ProfileReader
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
        super().__init__()

        self.recorder = Recorder()
        self.file_path = file_path

        self.events_buffer: list = []
        self.possible_shortcut = False

        self.pause: bool = False
        self.pause_toggle: bool = False

        self.record_thread = Thread(target=self.record)


    def start(self):
        self.record_thread.start()

        super().start()

        self.record_thread.join()


    def _update(self, event_code: ImportantEvents):
        super()._update(event_code)

        if event_code == ImportantEvents.TOGGLE:
            self.pause_toggle = True


    def record(self):
        with open(self.file_path, 'w') as file:
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


    def stop(self):
        self.recorder.stop()
        super().stop()
