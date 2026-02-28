from PIL import Image, ImageChops, ImageEnhance
import numpy as np
import cv2
from logging import getLogger


class Matcher:
    """
    Class responsible for comparing two images and deciding if they match
    and finding a template image in a larger one
    """
    def __init__(self, reference_image: Image.Image, total_diff_allowed: float = 5, individual_diff_allowed: int = 10,
                 mismatched_pixels_allowed: float = 0.1, brightness_diff_allowed: float = 10.0):
        """

        :param reference_image
        :param mismatched_pixels_allowed fraction of pixels that may not fit the match
        :param individual_diff_allowed maximum difference between the screenshot pixel and reference pixel
         in each colour, before the pixel is considered not matching
        :param total_diff_allowed maximum average difference, before the whole image is considered not matching
        """
        self.brightness_diff_allowed = brightness_diff_allowed
        self.reference_image: Image.Image = reference_image
        self.total_diff_allowed = total_diff_allowed
        self.individual_diff_allowed = individual_diff_allowed
        self.mismatched_pixels_allowed = mismatched_pixels_allowed

        self.logger = getLogger(__name__)


    @staticmethod
    def average_brightness(img: Image.Image) -> float:
        gray = img.convert("L")  # luminance
        return np.asarray(gray).mean()


    def match(self, screenshot: Image.Image) -> bool:
        reference_brightness = Matcher.average_brightness(self.reference_image)
        screenshot_brightness = Matcher.average_brightness(screenshot)

        if screenshot_brightness == 0:
            self.logger.debug(f"Screenshot brightness is 0")
            return False

        if abs(reference_brightness - screenshot_brightness) > self.brightness_diff_allowed:
            self.logger.debug(
                f"Match failed due to brightness diff {abs(reference_brightness - screenshot_brightness)} "
                f"max is {self.brightness_diff_allowed}"
            )
            return False

        enhancer = ImageEnhance.Brightness(screenshot)
        screenshot = enhancer.enhance(reference_brightness / screenshot_brightness)


        difference_image = ImageChops.difference(self.reference_image, screenshot)

        diff = np.asarray(difference_image)

        total_diff = diff.sum()
        mismatched_pixels = np.any(diff > self.individual_diff_allowed, axis=2).sum()

        total_pixels = screenshot.width * screenshot.height
        if total_diff / total_pixels > self.total_diff_allowed:
            self.logger.debug(
                f"Match failed due to average difference {total_diff / total_pixels},"
                f" max is {self.total_diff_allowed}")
            return False
        if mismatched_pixels / total_pixels > self.mismatched_pixels_allowed:
            self.logger.debug(
                f"Match failed due to mismatched pixels {mismatched_pixels / total_pixels},"
                f" max is {self.mismatched_pixels_allowed}")
            return False

        self.logger.info("Match successful")
        return True


    @staticmethod
    def convert_pil_image_to_cv(image: Image.Image):
        assert image.mode == "RGB"
        img_array = np.array(image)
        # img_cv = img_array[:, :, ::-1].copy()  # -1 does RGB -> BGR
        return cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)


    def find_match(self, screenshot: Image.Image, cached_reference_image = None) -> tuple[int, int, float]:
        """
        Find the best matching location of reference image in screenshot
        returns the center of the location and confidence

        Using OpenCV
        https://stackoverflow.com/questions/7670112/finding-a-subimage-inside-a-numpy-image/9253805#9253805
        https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html
        """
        res = cv2.matchTemplate(
            Matcher.convert_pil_image_to_cv(screenshot),
            cached_reference_image if cached_reference_image else Matcher.convert_pil_image_to_cv(self.reference_image),
            cv2.TM_CCOEFF_NORMED
        )

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        self.logger.debug(f"Template image found at {max_loc} with value {max_val}")
        return (int(max_loc[0] + self.reference_image.width / 2),
                int(max_loc[1] + self.reference_image.height / 2),
                max_val)