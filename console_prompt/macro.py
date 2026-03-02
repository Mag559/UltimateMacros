from prompt_toolkit.completion import PathCompleter

from macros import ClipboardMacro
from repeater import RecorderMacro, InterpreterMacro, MACRO_FILES
from .console_base import completer, default


macro_group = completer.group("macro")

@default
def _macro():
    print("Incomplete command.\nDescription:")
    print("Command for running macros.")


@macro_group.action("clipboard")
@completer.param(["2", "3", "5", "10", "100"], cast=int)
def _clipboard_macro(stack_size: int = 10):
    ClipboardMacro(stack_size).start()


@macro_group.action("recorder")
@completer.param(PathCompleter(False, lambda: [str(MACRO_FILES)], lambda path: path.endswith('.ins')), cast=str)
def _recorder_macro(file_name: str):
    RecorderMacro(MACRO_FILES / file_name).start()


@macro_group.action("interpreter")
@completer.param(PathCompleter(False, lambda: [str(MACRO_FILES)], lambda path: path.endswith('.ins')), cast=str)
def _interpreter_macro(file_name: str):
    if not file_name.endswith('.ins'):
        file_name += '.ins'
    InterpreterMacro(MACRO_FILES / file_name).start()