from macros import ClipboardMacro
from .console_base import completer, default

macro_group = completer.group("macro")

@default
def _macro():
    print("Incomplete command.\nDescription:")
    print("Command for running macros.")


@macro_group.action("clipboard")
@completer.param(["2", "3", "5", "10", "100"], cast=int)
@completer.param(["t"], cast=bool)
def _clipboard_makro(stack_size: int = 10, debug: bool = False):
    ClipboardMacro(stack_size, debug)
