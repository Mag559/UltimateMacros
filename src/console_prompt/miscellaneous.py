import os
from pathlib import Path

from prompt_toolkit.completion import PathCompleter

from src.profiles import PROFILES_PATH, ProfileReader
from .console_base import ConsoleBase
from .numpy_printer import NumpyPrinter

CURRENT_SEMESTER_DIR = Path("C:\\Users\\macie\\OneDrive\\Pulpit\\Pol\\4sem")


def setup_misc(console_base: ConsoleBase) -> None:
    completer = console_base.completer

    @completer.action("exit")
    @completer.action("quit")
    @completer.action("q")
    def _exit():
        quit(0)



    @completer.action("view")
    @completer.param([str(directory.name) for directory in CURRENT_SEMESTER_DIR.iterdir() if directory.is_dir()], cast=str)
    def _view(directory: str):
        printer: NumpyPrinter = NumpyPrinter()
        _display(CURRENT_SEMESTER_DIR / directory, 0, printer)
        console_base.toolbar.draw_on_canvas(printer.get_drawing(), 0, 0)


    def _display(directory: Path, indent: int, printer: NumpyPrinter):
        for item in (CURRENT_SEMESTER_DIR / directory).iterdir():
            if item.is_dir():
                printer.print(f"{indent * ' '} {item.name}:")

                _display(item, indent + 4, printer)
                continue

            if not item.name.endswith(".txt"):
                continue
            printer.print(f"{indent * ' '} {item.name}")

    @completer.action("notepad")
    @completer.param(PathCompleter(
        False,
        lambda: [str(CURRENT_SEMESTER_DIR)],
        lambda path: path.endswith('.txt') or (path.find(".") == -1)
    ), cast=str)
    def _notepad(file_name: str):
        console_base.focus_release()
        if not file_name.endswith('.txt'):
            file_name += '.txt'
        path_to_open = Path(CURRENT_SEMESTER_DIR / file_name)
        if not path_to_open.exists() or path_to_open.is_dir():
            return

        os.startfile(path_to_open)



    @completer.action("profile")
    @completer.param(
        [item.name.rstrip(".json") for item in PROFILES_PATH.iterdir() if item.name.endswith(".json")],
        cast=str
    )
    def _profile(profile: str = ""):
        if profile == "":
            ProfileReader.reload_profile()
        else:
            ProfileReader.switch_profile(profile)