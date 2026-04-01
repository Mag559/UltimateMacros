from pathlib import Path

import numpy as np
from prompt_toolkit.completion import PathCompleter

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

    # @completer.action("notepad")
    # @completer.param(PathCompleter(False, lambda: [str(MACRO_FILES)], lambda path: path.endswith('.txt')), cast=str)
    # def _interpreter_macro(file_name: str):
    #     if not file_name.endswith('.ins'):
    #         file_name += '.ins'
    #     InterpreterMacro(MACRO_FILES / file_name).start()