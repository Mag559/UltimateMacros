from threading import Thread
from pathlib import Path

from base_macro import BaseMacro
from .recorder import Recorder

class RecorderMacro(BaseMacro):
    """
    Macro version of the recorder

    """
    def __init__(self, file_path: Path, debug_mode: bool = False):
        self.recorder = Recorder()
        self.file_path = file_path

        self.record_thread = Thread(target=self.record)
        self.record_thread.start()
        super().__init__(debug_mode=debug_mode)
        self.record_thread.join()


    def record(self):
        with open(self.file_path, 'w') as file:
            for instruction in self.recorder.record():
                if self.debug_mode:
                    print(instruction)
                file.write(instruction + "\n")


    def terminate(self):
        self.recorder.stop()
        super().terminate()
