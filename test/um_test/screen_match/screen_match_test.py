import unittest
from pathlib import Path

from PIL import Image

from um.screen_match import Section, ScreenMatch
from um_test.screen_match.mock_capturer import MockCapturer, MockMss

TEST_RESOURCES_DIR = Path(__file__).resolve().parents[2] / "resources"


def before_grab(calls: list[int], mock_mss: MockMss, total_calls: int, replacement_img):
    if calls[0] == total_calls - 1:
        mock_mss.img = replacement_img
    calls[0] += 1


class ScreenMatchTest(unittest.TestCase):
    def test_wait_for_match(self):
        fake_img = Image.open(TEST_RESOURCES_DIR / "fake_desktop.png")
        screen_match: ScreenMatch = ScreenMatch() \
            .set_total_diff_allowed(0.1) \
            .set_individual_diff_allowed(1) \
            .set_mismatched_pixels_allowed(0.01) \
            .set_brightness_diff_allowed(1)

        calls = [0]
        mock_mss = MockMss(before_grab=lambda: before_grab(calls, mock_mss, 3, fake_img))

        screen_match.capturer = MockCapturer(Section(0, 0, 1920, 1080), mock_mss)

        screen_match.load_reference_image(TEST_RESOURCES_DIR / "fake_icons.png")
        self.assertTrue(screen_match.wait_for_match(0.09, 0.03))
        self.assertEqual(3, calls[0])

    def test_wait_for_find_match(self):
        with open(TEST_RESOURCES_DIR / "fake_icons.txt", "r") as f:
            correct_section = Section.from_string(f.readline().strip('\n'))

        fake_img = Image.open(TEST_RESOURCES_DIR / "fake_desktop.png")
        screen_match: ScreenMatch = ScreenMatch() \
            .set_total_diff_allowed(0.1) \
            .set_individual_diff_allowed(1) \
            .set_mismatched_pixels_allowed(0.01) \
            .set_brightness_diff_allowed(1)

        calls = [0]
        mock_mss = MockMss(before_grab=lambda: before_grab(calls, mock_mss, 3, fake_img))

        screen_match.capturer = MockCapturer(Section(0, 0, 1920, 1080), mock_mss)

        screen_match.load_reference_image(TEST_RESOURCES_DIR / "fake_icons.png")
        screen_match.set_compared_section(Section(0, 0, 1920, 1080))

        result = screen_match.wait_for_find_match(0.09, 0.03)
        self.assertTrue(isinstance(result, tuple))
        self.assertEqual(3, calls[0])
        self.assertAlmostEqual(correct_section.left + correct_section.width / 2, result[0], delta=3)
        self.assertAlmostEqual(correct_section.top + correct_section.height / 2, result[1], delta=3)


if __name__ == '__main__':
    unittest.main()
