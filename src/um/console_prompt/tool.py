from .console_base import ConsoleBase
import um.tools
from .numpy_printer import NumpyPrinter


def setup_tool(console_base: ConsoleBase) -> None:
    """
    Register actions for running tools.
    :param console_base: a bridge to some of the console Main's functionality
    :return:
    """
    tool_group = console_base.completer.group("tool")

    @console_base.default
    def _tool():
        printer: NumpyPrinter = NumpyPrinter()
        printer.print("command group for running tools")
        printer.print("")
        printer.print("type `tool + space bar`")
        printer.print("for autocomplete to list")
        printer.print("the available tools")
        printer.print("")
        printer.print("also see the reference")
        printer.print("at docs/actions.md")
        console_base.toolbar.draw_on_canvas(printer.get_drawing(), 0, 0)

    @tool_group.action("screenshot_preview")
    def _screenshot_preview():
        um.tools.ScreenshotPreview().start()
