from pathlib import Path
from PIL import Image

from um.profiles import ProfileReader
import um.base_macro
import um.screen_match


class ScreenshotMacro(um.base_macro.BaseMacro):
    """
    SHORTCUT2 -> take screenshot and save it in the specified path

    3x Alt + ` in quick succession -> exit the macro
    """

    def __init__(self,
                 save_path: str | Path,
                 monitor_number: int = ProfileReader.profile().macro_screenshot_monitor,
                 section: str = ProfileReader.profile().macro_screenshot_section
                 ):
        """
        :param save_path: directory to save the screenshots in
        :param monitor_number: which monitor to take screenshots of
        :param section: section of the screen to take screenshots of
        """
        super().__init__(status_window_kwargs={
            "name": "ScreenshotMacro",
            "state": "running",
            "details": f""
        })

        self._capturer: um.screen_match.Capturer = um.screen_match.Capturer(
            um.screen_match.Section.from_string(section),
            monitor_number
        )
        self.save_path: Path = save_path if save_path is Path else Path(save_path)
        self._idx: int = sum(1 for _ in self.save_path.glob('*.png'))

    def _update(self, event_code: um.base_macro.ImportantEvent) -> bool:
        """
        Handle clipboard-related important events
        :param event_code: The clipboard event to handle (SHORTCUT1, SHORTCUT2, or PASTE are handled).
        :return: True if the macro was terminated, false otherwise
        """
        match event_code:
            case um.base_macro.ImportantEvent.SHORTCUT2:
                image: Image.Image = self._capturer.capture_screenshot()
                path = self.save_path / f"{self._idx:02d}.png"
                image.save(path)
                self._idx += 1

                self.status_window.set_details(
                    f"Screenshot saved at {path}"
                )
            case _:
                self.status_window.set_details(
                    f""
                )

        return super()._update(event_code)

