from time import sleep
from pathlib import Path
from PIL import Image
from logging import getLogger

from um.profiles import ProfileReader
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

    def check_match(self) -> bool:
        return self.matcher.match(self.capturer.capture_screenshot())

    def wait_for_match(
            self,
            timeout: float = ProfileReader.profile().match_wait_timeout,
            interval: float = ProfileReader.profile().match_wait_check_interval
    ) -> bool:
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
            self.logger.debug(f"{i}th match failed")
            sleep(interval)
        self.logger.warning("Screen matching timeout out")
        self.capturer.capture_screenshot().save("match_failed.png")
        return False

    def find_match(
            self,
            confidence_required: float = ProfileReader.profile().match_confidence,
            cached_reference=None
    ) -> tuple[int, int] | bool:
        pos_x, pos_y, confidence = self.matcher.find_match(self.capturer.capture_screenshot(), cached_reference)
        if confidence >= confidence_required:
            return pos_x, pos_y
        return False

    def wait_for_find_match(
            self,
            timeout: float = ProfileReader.profile().match_wait_timeout,
            interval: float = ProfileReader.profile().match_wait_check_interval,
            confidence_required: float = ProfileReader.profile().match_confidence
    ) -> tuple[int, int] | bool:
        """
        Call find match periodically
        Parameters:
            interval: float how many seconds to wait between checks
            timeout: float how many seconds to wait before giving up
            confidence_required: float minimal confidence in the match for it to be accepted
        Returns:
            Coordinates of the center of the matched image
            if a match happens before timeout, False otherwise
        """
        cached_reference = Matcher.convert_pil_image_to_cv(self.matcher.reference_image)

        for i in range(round(timeout / interval)):
            match_found = self.find_match(confidence_required, cached_reference)
            if match_found:
                return match_found
            self.logger.debug(f"{i}th find match failed")
            sleep(interval)
        self.logger.warning("Screen find matching timeout out")
        self.capturer.capture_screenshot().save("match_failed.png")
        return False

    def set_reference_image(self, reference_image: Image.Image) -> 'ScreenMatch':
        self.matcher.reference_image = reference_image
        return self

    def load_reference_image(self, image_path: Path) -> 'ScreenMatch':
        with Image.open(image_path) as image:
            self.set_reference_image(image.copy())

        section_file = image_path.with_suffix('.txt')
        if not section_file.exists():
            return self

        with open(section_file, 'r') as f:
            self.set_compared_section(
                Section.from_string(f.readline().strip('\n'))
            )
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
