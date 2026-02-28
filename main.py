import logging
import ctypes
from console_prompt import main


PROCESS_PER_MONITOR_DPI_AWARE = 2

ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)



if __name__ == "__main__":
    logging.basicConfig(filename='myapp.log', level=logging.DEBUG)
    main()
