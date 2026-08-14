from .console_base import ConsoleBase
import um.tools


def setup_tool(console_base: ConsoleBase) -> None:
    """
    Register actions for running tools.
    :param console_base: a bridge to some of the console Main's functionality
    :return:
    """
    tool_group = console_base.completer.group("tool")

    @console_base.default
    def _tool():
        print("Command for running tools.")

    @tool_group.action("screenshot_preview")
    def _screenshot_preview():
        um.tools.ScreenshotPreview().start()
