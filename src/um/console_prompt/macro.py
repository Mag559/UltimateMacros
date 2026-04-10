from prompt_toolkit.completion import PathCompleter

from um.macros import ClipboardMacro
from um.repeater import RecorderMacro, InterpreterMacro, RepeaterMacro, MACRO_FILES
from .console_base import ConsoleBase


def setup_macro(console_base: ConsoleBase) -> None:
    macro_group = console_base.completer.group("macro")
    macro_files_completer: PathCompleter = PathCompleter(
        False,
        lambda: [str(MACRO_FILES)],
        lambda path: path.endswith('.ins')
    )

    @console_base.default
    def _macro():
        print("Incomplete command.\nDescription:")
        print("Command for running macros.")


    @macro_group.action("clipboard")
    @console_base.completer.param(["2", "3", "5", "10", "100"], cast=int)
    def _clipboard_macro(stack_size: int = 10):
        console_base.focus_release()
        macro: ClipboardMacro = ClipboardMacro(stack_size)
        macro.start()



    @macro_group.action("recorder")
    @console_base.completer.param(macro_files_completer, cast=str)
    def _recorder_macro(file_name: str):
        console_base.focus_release()
        RecorderMacro(MACRO_FILES / file_name).start()


    @macro_group.action("interpreter")
    @console_base.completer.param(macro_files_completer, cast=str)
    def _interpreter_macro(file_name: str):
        console_base.focus_release()
        if not file_name.endswith('.ins'):
            file_name += '.ins'
        InterpreterMacro(MACRO_FILES / file_name).start()

    @macro_group.action("repeater")
    def _repeater_macro():
        console_base.focus_release()
        RepeaterMacro().start()