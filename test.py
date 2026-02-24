import logging
from pathlib import Path
from time import sleep, time

from base_macro import BaseMacro
from repeater import Recorder, build_file_interpreter, RecorderMacro
import ctypes


PROCESS_PER_MONITOR_DPI_AWARE = 2

ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)

if __name__ == '__main__':
    logging.basicConfig(filename='myapp.log', level=logging.DEBUG)
    RecorderMacro(Path(__file__).parent / 'test.ins')



    # print("Recording done")
    # sleep(2)

    # build_file_interpreter(Path('test.ins'))