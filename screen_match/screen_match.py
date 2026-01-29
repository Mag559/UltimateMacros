from PIL import Image
from capturer import Capturer, Section
from matcher import Matcher
from pathlib import Path


class ScreenMatch:
    """
    Determines whether a specified section of the screenshot
    is similar to the provided reference image
    """
    def __init__(self) -> None:
        self.capturer: Capturer = Capturer(Section(0, 0, 10, 10))
        self.matcher: Matcher = Matcher(Image.new("RGB", (1, 1), color=(255, 255, 255)))


    def check_match(self):
        return self.matcher.match(self.capturer.capture_screenshot())


    def set_reference_image(self, reference_image: Image) -> 'ScreenMatch':
        self.matcher.reference_image = reference_image
        return self


    def load_reference_image(self, image_path: Path) -> 'ScreenMatch':
        with Image.open(image_path) as image:
            self.set_reference_image(image)
        return self


    def set_monitor_number(self, monitor_number: int) -> 'ScreenMatch':
        self.capturer.monitor_number = monitor_number
        return self


    def set_compared_section(self, compared_section: tuple[int, int, int, int]) -> 'ScreenMatch':
        self.capturer.section = compared_section
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




if __name__ == "__main__":
    print("Hello")