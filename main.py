import logging
import ctypes
from console_prompt import main
from sys import stdout


# have a unified coordinate system for pynput mouse movement and detection (no scale)
PROCESS_PER_MONITOR_DPI_AWARE = 2
ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)



if __name__ == "__main__":
    logging.basicConfig(filename='myapp.log', level=logging.DEBUG)
    # send a signal, that you want to receive an event when console is unfocused
    stdout.write('\x1b[?1004h')
    stdout.flush()
    main()
    stdout.write('\x1b[?1004l')
    stdout.flush()
