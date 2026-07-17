from time import sleep

from .preview_window import PreviewWindow
from um.profiles import ProfileReader
from um.screen_match import Capturer, Section, REFERENCE_IMAGES


class ScreenshotPreview:
    def __init__(self):
        self.capturer = Capturer(Section(100, 100, 100, 100))
        self.window = PreviewWindow(self.capturer.capture_screenshot(), self.save)

    def start(self):
        self.schedule_next_update()
        self.window.mainloop()

    def schedule_next_update(self):
        # noinspection PyTypeChecker
        self.window.after(
            int(ProfileReader.profile().screenshot_preview_spf * 100),
            self.update
        )

    def update(self):
        self.capturer.set_section(self.get_section())
        self.window.set_image(self.capturer.capture_screenshot())
        self.schedule_next_update()

    def get_section(self):
        """
        Converts left, top, width, height to a Section object.
        """
        return Section(*[max(q, 1) for q in self.window.get_all_numbers()])

    def save(self, name):
        sleep(ProfileReader.profile().screenshot_delay_before_save)
        self.capturer.capture_screenshot().save(
            REFERENCE_IMAGES / f"{name}.png",
            "PNG"
        )
        with open(REFERENCE_IMAGES / f"{name}.txt", "w") as f:
            f.write(",".join([str(x) for x in self.window.get_all_numbers()]))
        self.window.destroy()
