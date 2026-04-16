import logging
import ctypes

from um import main, ProfileReader
from sys import stdout


# have a unified coordinate system for pynput mouse movement and detection (no scale)
PROCESS_PER_MONITOR_DPI_AWARE = 2
ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)



if __name__ == "__main__":
    logging.basicConfig(
        filename='myapp.log',
        level=ProfileReader.profile().logging_level
    )


    # send a signal, that you want to receive an event when console is unfocused
    stdout.write('\x1b[?1004h')
    stdout.flush()
    try:
        main()
    except SystemExit as e:
        stdout.write('\x1b[?1004l')
        stdout.flush()
        raise e
