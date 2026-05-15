import logging
import ctypes
from pathlib import Path


from um import main, ProfileReader
from sys import stdout


# have a unified coordinate system for pynput mouse movement and detection (no scale)
PROCESS_PER_MONITOR_DPI_AWARE = 2
ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)

PROJECT_ROOT = Path(__file__).parents[2]


def clean_logs():
    log_path = PROJECT_ROOT / "myapp.log"
    metalog_path = PROJECT_ROOT / "myapp_meta.log"

    initial_log_size: int = log_path.stat().st_size
    if initial_log_size < ProfileReader.profile().logging_min_size_to_clean:
        # not big enough to warrant cleaning
        return

    # remove lines until (slightly) less than desired is left
    deleted_lines: int = 0
    with open(log_path, "rb+") as log_file:
        for _ in log_file:
            deleted_lines += 1
            if log_file.tell() >= initial_log_size - ProfileReader.profile().logging_uncleaned_size:
                break

        rest = log_file.read()
        log_file.seek(0)
        log_file.truncate(len(rest))
        log_file.write(rest)

    # log the removal stats
    with open(metalog_path, "r+") as meta_log_file:
        stats: dict[str, int] = {
            "BytesDeleted": 0,
            "LinesDeleted": 0
        }
        for line in meta_log_file:
            key, value = line.split(":", maxsplit=1)
            stats[key] = int(value)

        stats["BytesDeleted"] += initial_log_size - log_path.stat().st_size
        stats["LinesDeleted"] += deleted_lines

        meta_log_file.seek(0)
        meta_log_file.truncate(0)

        meta_log_file.writelines([f"{name}:{value:_}\n" for name, value in stats.items()])


if __name__ == "__main__":
    clean_logs()

    logging.basicConfig(
        filename='myapp.log',
        level=ProfileReader.profile().logging_level
    )


    # send a signal, that you want to receive an event when console is unfocused
    stdout.write('\x1b[?1004h')
    stdout.flush()
    try:
        main()
    except SystemExit:
        stdout.write('\x1b[?1004l')
        stdout.flush()
        raise
