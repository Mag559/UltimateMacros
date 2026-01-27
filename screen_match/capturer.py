from PIL import Image
from mss import mss


class Capturer:
    """
    Captures a specified part of the screen
    """
    def __init__(self, section: tuple[int, int, int, int], monitor_number: int = 0):
        self.monitor = None
        try:
            self.capturer = mss()
        except Exception:
            raise RuntimeError("Screen capturing by mss failed")

        self.set_monitor(monitor_number)
        self.section = section


    def set_monitor(self, monitor_number: int) -> None:
        # Get information of the specified monitor
        mon = self.capturer.monitors[monitor_number]

        # The screen part to capture
        self.monitor = {
            "top": mon["top"],
            "left": mon["left"],
            "width": mon["width"],
            "height": mon["height"],
            "mon": monitor_number,
        }


    def capture_screenshot(self) -> Image.Image:
        screenshot = self.capturer.grab(self.monitor)
        image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        return image.crop(self.section)



if __name__ == "__main__":
    pass