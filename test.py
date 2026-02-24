import logging
from pathlib import Path
from time import sleep, time

from base_macro import BaseMacro
from repeater import Recorder, build_file_interpreter
import ctypes


PROCESS_PER_MONITOR_DPI_AWARE = 2

ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)

if __name__ == '__main__':


    logging.basicConfig(filename='myapp.log', level=logging.DEBUG)

    # last_ins_time = 0
    # recorder = Recorder()
    # with open('test.ins', 'w') as f:
    #     for instruction in recorder.record():
    #         if last_ins_time != 0 and time() - last_ins_time > 5:
    #             recorder.stop()
    #             break
    #         last_ins_time = time()
    #         print(instruction)
    #         f.write(instruction + "\n")


    print("Recording done")
    sleep(2)

    build_file_interpreter(Path('test.ins'))