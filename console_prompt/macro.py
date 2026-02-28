from pathlib import Path

from macros import ClipboardMacro
from repeater import RecorderMacro, InterpreterMacro
from .console_base import completer, default

MACRO_FILES = Path(__file__).parent.parent / "macro_files"

macro_group = completer.group("macro")

@default
def _macro():
    print("Incomplete command.\nDescription:")
    print("Command for running macros.")


@macro_group.action("clipboard")
@completer.param(["2", "3", "5", "10", "100"], cast=int)
@completer.param(["t"], cast=bool)
def _clipboard_macro(stack_size: int = 10, debug: bool = False):
    ClipboardMacro(stack_size, debug)


@macro_group.action("recorder")
@completer.param(None, cast=str)
@completer.param(["t"], cast=bool)
def _recorder_macro(file_name: str, debug: bool = False):
    RecorderMacro(MACRO_FILES / file_name, debug)


@macro_group.action("interpreter")
@completer.param(None, cast=str)
@completer.param(["t"], cast=bool)
def _interpreter_macro(file_name: str, debug: bool = False):
    InterpreterMacro(MACRO_FILES / file_name, debug)