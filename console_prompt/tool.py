from tools import ScreenshotPreview
from .console_base import completer, default

tool_group = completer.group("tool")

@default
def _tool():
    print("Incomplete command.\nDescription:")
    print("Command for running tools.")


@tool_group.action("screenshot_preview")
def _screenshot_preview():
    ScreenshotPreview().start()
