import re
from threading import Thread
from pathlib import Path

from base_macro import BaseMacro
from .recorder import Recorder

class RecorderMacro(BaseMacro):
    """
    Macro version of the recorder
    Filters out SHORTCUT1
    """
    def __init__(self, file_path: Path, debug_mode: bool = False):
        self.recorder = Recorder()
        self.file_path = file_path
        self.events_buffer: list = []
        self.possible_shortcut = False

        self.record_thread = Thread(target=self.record)
        self.record_thread.start()
        super().__init__(debug_mode=debug_mode)
        self.record_thread.join()


    def record(self):
        with open(self.file_path, 'w') as file:
            for instruction in self.recorder.record():
                if self.debug_mode:
                    print(instruction)

                # if ` is pressed next it's a shortcut, so have to start buffering
                if re.search(r".*press alt_l*$", instruction):
                    self.possible_shortcut = True
                    self.events_buffer.append(instruction)
                    continue

                # no possible shortcut rn
                if not self.possible_shortcut:
                    file.write(instruction + "\n")
                    continue

                # it was a shortcut, cut it out
                if re.search(r".*release alt_l*$", instruction) and len(self.events_buffer) > 0:
                    self.possible_shortcut = False
                    self.events_buffer.clear()
                    continue

                self.events_buffer.append(instruction)

                # not the shortcut after all, write the buffered inputs into the file
                if not re.search(r".*`*$", instruction):
                    self.possible_shortcut = False
                    for event in self.events_buffer:
                        file.write(event + "\n")
                    self.events_buffer.clear()


    def terminate(self):
        self.recorder.stop()
        super().terminate()
