from src.tools import ScreenshotPreview
from .console_base import ConsoleBase

def setup_tool(console_base: ConsoleBase) -> None:
    tool_group = console_base.completer.group("tool")

    @console_base.default
    def _tool():
        print("Incomplete command.\nDescription:")
        print("Command for running tools.")


    @tool_group.action("screenshot_preview")
    def _screenshot_preview():
        ScreenshotPreview().start()
