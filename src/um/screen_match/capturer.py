from dataclasses import dataclass
from logging import getLogger
from PIL import Image
from mss import MSS

from um.profiles import ProfileReader


@dataclass
class Section:
    """
    Dataclass representing the geometry of a rectangular screen section.
    """
    left: int
    top: int
    width: int
    height: int

    @staticmethod
    def to_string(section: Section) -> str:
        """
        Serialization to string
        """
        return f"{section.left},{section.top},{section.width},{section.height}"

    @staticmethod
    def from_string(section: str) -> Section:
        """
        Deserialization from a string
        """
        return Section(*[int(x) for x in section.strip(' ').split(',')])

    @property
    def centre(self) -> tuple[int, int]:
        """
        Get the centre of the rectangular section.
        """
        return int(self.left + self.width / 2), int(self.top + self.height / 2)


class Capturer:
    """
    Captures a specified part of the screen
    and returns it as a PIL Image object.
    """

    def __init__(
            self,
            section: Section,
            monitor_number: int = ProfileReader.profile().match_monitor_number,
            capturer_override=None
    ):
        """
        :param section: what section of the screen to capture, can be changed later
        :param monitor_number: which monitor to capture from
        :param capturer_override: optional override of the mss screenshot taker
        :return:
        """
        self.monitor = None
        self.monitor_number = monitor_number
        self.logger = getLogger(__name__)
        if capturer_override:
            self.capturer = capturer_override
        else:
            try:
                self.capturer = MSS()
            except Exception as e:
                self.logger.exception("Screen capturing by mss failed")
                raise RuntimeError(e)

        self.section = section
        self.set_monitor(monitor_number)
        self.logger.debug("Capturer initialized")

    def set_section(self, section: Section) -> None:
        """
        Update the captured section
        :param section: what section of the screen to capture
        :return:
        """
        self.section = section
        self.logger.debug(f"Section updated to: {section}")
        self.set_monitor(self.monitor_number)

    def set_monitor(self, monitor_number: int) -> None:
        """
        Update the captured monitor and recalculate the parameters used for grabbing the screenshot.
        :param monitor_number: which monitor to capture
        :return:
        """
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
        self.logger.debug(f"Monitor updated to: {self.monitor}")

    def capture_screenshot(self) -> Image.Image:
        """
        Ask the capturer for a screenshot and convert it to a PIL Image object.
        :return: screenshot as a PIL Image
        """
        screenshot = self.capturer.grab(self.monitor)
        self.logger.debug(f"Screenshot captured: {screenshot.size}")
        return Image.frombytes(
            "RGB",
            (screenshot.size.width, screenshot.size.height),
            screenshot.rgb
        )
