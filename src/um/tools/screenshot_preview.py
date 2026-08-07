from time import sleep

from .preview_window import PreviewWindow
from um.profiles import ProfileReader
from um.screen_match import Capturer, Section, REFERENCE_IMAGES


class ScreenshotPreview:
    """
    Tkinter based window for previewing a screenshot of set size and position.
    Tkinter code is in the PreviewWindow class,
    this acts as a middle man between it, Capturer of the screenshot and saving.
    """
    def __init__(self):
        self.capturer = Capturer(Section(100, 100, 100, 100))
        self.window = PreviewWindow(self.capturer.capture_screenshot(), self.save)

    def start(self) -> None:
        """
        Starts the preview window.
        """
        self._schedule_next_update()
        self.window.mainloop()

    def _schedule_next_update(self) -> None:
        """
        One time hook up of ``update`` to be triggered by tkinter.
        Effectively sets the refresh rate of the screenshot to `screenshot_preview_spf` in the profile.
        """
        # noinspection PyTypeChecker
        self.window.after(
            int(ProfileReader.profile().screenshot_preview_spf * 1000),
            self._update
        )

    def _update(self) -> None:
        """
        Refresh the screenshot and schedule next update.
        """
        self.capturer.set_section(self.get_section())
        self.window.set_image(self.capturer.capture_screenshot())
        self._schedule_next_update()

    def get_section(self) -> Section:
        """
        Converts left, top, width, height to a Section object.
        """
        return Section(*[max(q, 1) for q in self.window.get_all_numbers()])

    def save(self, name) -> None:
        """
        Take and save the screenshot of the selected section.
        Features a delay of `screenshot_delay_before_save` for situations requiring focus of the screenshotted window.
        """
        sleep(ProfileReader.profile().screenshot_delay_before_save)
        self.capturer.capture_screenshot().save(
            REFERENCE_IMAGES / f"{name}.png",
            "PNG"
        )
        with open(REFERENCE_IMAGES / f"{name}.txt", "w") as f:
            f.write(",".join([str(x) for x in self.window.get_all_numbers()]))
        self.window.destroy()
