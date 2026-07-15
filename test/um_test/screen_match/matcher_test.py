import unittest
from pathlib import Path

from PIL import Image

from um.screen_match import Matcher, Section

TEST_RESOURCES_DIR = Path(__file__).resolve().parents[2] / "resources"


class MatcherTest(unittest.TestCase):
    def test_match(self):
        img = Image.open(TEST_RESOURCES_DIR / "desktop.png")
        fake_img = Image.open(TEST_RESOURCES_DIR / "fake_desktop.png")
        matcher: Matcher = Matcher(
            img,
            0.1,
            1,
            0.01,
            1
        )
        self.assertTrue(matcher.match(img))
        self.assertFalse(matcher.match(fake_img))

    def test_find_match(self):
        img = Image.open(TEST_RESOURCES_DIR / "desktop.png")
        icon_to_find = Image.open(TEST_RESOURCES_DIR / "desktop_icon.png")

        with open(TEST_RESOURCES_DIR / "desktop_icon.txt", "r") as f:
            correct_section = Section.from_string(f.readline().strip('\n'))

        matcher: Matcher = Matcher(
            icon_to_find,
            0.1,
            1,
            0.01,
            1
        )
        guess = matcher.find_match(img)
        self.assertAlmostEqual(guess[0], correct_section.left + correct_section.width / 2, delta=3)
        self.assertAlmostEqual(guess[1], correct_section.top + correct_section.height / 2, delta=3)
        self.assertGreater(guess[2], 0.95)


if __name__ == '__main__':
    unittest.main()
