from PIL import Image

class Matcher:
    """
    Component of ScreenMatch, responsible for comparing two pixel matrices
    """
    def __init__(self, reference_image: Image.Image, total_diff_allowed: float = 5, individual_diff_allowed: int = 10,
                 mismatched_pixels_allowed: float = 0.1):
        """

        :param reference_image
        :param mismatched_pixels_allowed fraction of pixels that may not fit the match
        :param individual_diff_allowed maximum difference between the screenshot pixel and reference pixel
         in each colour, before the pixel is considered not matching
        :param total_diff_allowed maximum average difference, before the whole image is considered not matching
        """
        self.reference_image = reference_image
        self.total_diff_allowed = total_diff_allowed
        self.individual_diff_allowed = individual_diff_allowed
        self.mismatched_pixels_allowed = mismatched_pixels_allowed


    def match(self, screenshot: Image.Image) -> bool:
        total_pixels = screenshot.width * screenshot.height
        total_diff = 0
        mismatched_pixels = 0
        for i in range(screenshot.width):
            for j in range(screenshot.height):
                pixel = screenshot.pixel(j, i)
                reference_pixel = self.reference_image.pixel(j, i)
                for colour, ref_colour in zip(pixel, reference_pixel):
                    diff = abs(colour - ref_colour)
                    total_diff += diff
                    if diff > self.individual_diff_allowed:
                        mismatched_pixels += 1

        if total_diff / total_pixels > self.total_diff_allowed:
            return False
        if mismatched_pixels / total_pixels > self.mismatched_pixels_allowed:
            return False
        return True