from pathlib import Path

from prompt_toolkit.completion import PathCompleter

import um.macros
import um.repeater
from um.profiles import MACRO_FILES
from .console_base import ConsoleBase
from .numpy_printer import NumpyPrinter
from .path_completer import UmPathCompleter, resolve_autocompleted_path
from .. import ProfileReader


def setup_macro(console_base: ConsoleBase) -> None:
    """
    Register actions for running macros.
    :param console_base: a bridge to some of the console Main's functionality
    :return:
    """
    macro_group = console_base.completer.group("macro")
    macro_files_completer: PathCompleter = PathCompleter(
        False,
        lambda: [str(MACRO_FILES)],
        lambda path: path.endswith('.ins')
    )

    @console_base.default
    def _macro():
        printer: NumpyPrinter = NumpyPrinter()
        printer.print("command group for running macros")
        printer.print("")
        printer.print("type `macro + space bar`")
        printer.print("for autocomplete to list")
        printer.print("the available macros")
        printer.print("")
        printer.print("also see the reference")
        printer.print("at docs/actions.md")
        console_base.toolbar.draw_on_canvas(printer.get_drawing(), 0, 0)

    @macro_group.action("clipboard")
    @console_base.completer.param(["2", "3", "5", "10", "100"], cast=int)
    def _clipboard_macro(stack_size: int = 10):
        console_base.focus_release()
        macro: um.macros.ClipboardMacro = um.macros.ClipboardMacro(stack_size)
        macro.start()

    @macro_group.action("pinned")
    def _pinned_macro():
        console_base.focus_release()
        macro: um.macros.PinnedClipboardMacro = um.macros.PinnedClipboardMacro()
        macro.start()

    @macro_group.action("screenshot")
    @console_base.completer.param(
        UmPathCompleter(only_directories=True),
        cast=str
    )
    @console_base.completer.param(
        ["1", "2"],
        cast=int
    )
    def _screenshot_macro(
            str_directory: str,
            monitor: int = ProfileReader.profile().macro_screenshot_monitor
    ):
        console_base.focus_release()

        directory: Path = resolve_autocompleted_path(str_directory)
        if not directory.exists():
            return

        macro: um.macros.ScreenshotMacro = um.macros.ScreenshotMacro(
            directory,
            monitor
        )
        macro.start()

    @macro_group.action("recorder")
    @console_base.completer.param(macro_files_completer, cast=str)
    def _recorder_macro(file_name: str):
        console_base.focus_release()
        um.repeater.RecorderMacro(file_name).start()

    @macro_group.action("interpreter")
    @console_base.completer.param(macro_files_completer, cast=str)
    def _interpreter_macro(file_name: str):
        console_base.focus_release()
        um.repeater.InterpreterMacro(file_name).start()

    @macro_group.action("repeater")
    def _repeater_macro():
        console_base.focus_release()
        um.repeater.RepeaterMacro().start()

    @macro_group.action("textmap")
    def _text_map_macro():
        console_base.focus_release()
        um.macros.TextMapMacro(lambda x: um.macros.surround_with(x, "$\\texttt{", "}$")).start()
