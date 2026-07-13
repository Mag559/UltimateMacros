from pathlib import Path

from PIL import Image

from um.screen_match import Capturer, Section

TEST_RESOURCES_DIR = Path(__file__).resolve().parents[2] / "resources"
TEST_MONITOR_RESOLUTION = (1920, 1080)

class MockMss:
    def __init__(self) -> None:
        self.img_path = TEST_RESOURCES_DIR / "desktop.png"
        self.img = Image.open(self.img_path).copy()


    def grab(self, monitor: dict[str, int]):
        return self.img.crop(
            (
                monitor["left"],
                monitor["top"],
                monitor["left"] + monitor["width"],
                monitor["top"] + monitor["height"]
            )
        )


    @property
    def monitors(self) -> list[dict[str, int]]:
        return [
            {
                'left': 0,
                'top': 0,
                'width': TEST_MONITOR_RESOLUTION[0],
                'height': TEST_MONITOR_RESOLUTION[1]
            } for _ in range(2)
        ]


class MockCapturer(Capturer):
    def __init__(self, section: Section):
        super().__init__(section, monitor_number=0, capturer_override=MockMss())


    def capture_screenshot(self) -> Image.Image:
        return self.capturer.grab(self.monitor)

