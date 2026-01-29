from dataclasses import dataclass

from PIL import Image
from mss import mss

@dataclass
class Section:
    left: int
    top: int
    width: int
    height: int


class Capturer:
    """
    Captures a specified part of the screen
    """
    def __init__(self, section: Section, monitor_number: int = 0):
        """
        :section: Section left, top, width, height
        :monitor_number: int
        """
        self.monitor = None
        self.monitor_number = monitor_number
        try:
            self.capturer = mss()
        except Exception:
            raise RuntimeError("Screen capturing by mss failed")

        self.section = section
        self.set_monitor(monitor_number)


    def set_section(self, section: Section):
        self.section = section
        self.set_monitor(self.monitor_number)


    def set_monitor(self, monitor_number: int) -> None:
        # Get information of the specified monitor
        mon = self.capturer.monitors[monitor_number]

        # The screen part to capture
        self.monitor = {
            "top": mon["top"] + self.section.top,
            "left": mon["left"] + self.section.left,
            "width": self.section.width,
            "height": self.section.height,
            "mon": monitor_number,
        }


    def capture_screenshot(self) -> Image.Image:
        screenshot = self.capturer.grab(self.monitor)
        return Image.frombytes(
            "RGB",
            screenshot.size,
            screenshot.rgb
        )



if __name__ == "__main__":
    pass