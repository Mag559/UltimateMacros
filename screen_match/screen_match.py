from time import sleep
from pathlib import Path
from PIL import Image
from logging import getLogger

from .capturer import Capturer, Section
from .matcher import Matcher


class ScreenMatch:
    """
    Determines whether a specified section of the screenshot
    is similar to the provided reference image
    """
    def __init__(self) -> None:
        self.capturer: Capturer = Capturer(Section(0, 0, 10, 10))
        self.matcher: Matcher = Matcher(Image.new("RGB", (1, 1), color=(255, 255, 255)))
        self.logger = getLogger(__name__)


    def check_match(self):
        return self.matcher.match(self.capturer.capture_screenshot())

    def wait_for_match(self, timeout: float=10.0, interval: float=0.2) -> bool:
        """
        Call check match periodically
        Parameters:
            interval: float how many seconds to wait between checks
            timeout: float how many seconds to wait before giving up
        Returns:
            True if a match happens before timeout, False otherwise
        """
        for i in range(round(timeout / interval)):
            if self.check_match():
                return True
            self.logger.info(f"{i}th match failed")
            sleep(interval)
        self.logger.warning("Screen matching timeout out")
        self.capturer.capture_screenshot().save("match_failed.png")
        return False


    def set_reference_image(self, reference_image: Image.Image) -> 'ScreenMatch':
        self.matcher.reference_image = reference_image
        return self


    def load_reference_image(self, image_path: Path) -> 'ScreenMatch':
        with Image.open(image_path) as image:
            self.set_reference_image(image.copy())
        return self


    def set_monitor_number(self, monitor_number: int) -> 'ScreenMatch':
        self.capturer.monitor_number = monitor_number
        return self


    def set_compared_section(self, compared_section: Section) -> 'ScreenMatch':
        self.capturer.set_section(compared_section)
        return self


    def set_total_diff_allowed(self, total_diff_allowed: float) -> 'ScreenMatch':
        self.matcher.total_diff_allowed = total_diff_allowed
        return self


    def set_individual_diff_allowed(self, individual_diff_allowed: int) -> 'ScreenMatch':
        self.matcher.individual_diff_allowed = individual_diff_allowed
        return self


    def set_mismatched_pixels_allowed(self, mismatched_pixels_allowed: float) -> 'ScreenMatch':
        self.matcher.mismatched_pixels_allowed = mismatched_pixels_allowed
        return self

    def set_brightness_diff_allowed(self, brightness_diff_allowed: float) -> 'ScreenMatch':
        self.matcher.brightness_diff_allowed = brightness_diff_allowed
        return self



if __name__ == "__main__":
    print("Hello")