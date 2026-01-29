from pathlib import Path
from preview_window import PreviewWindow
from screen_match.capturer import Capturer, Section


class ScreenshotPreview:
    def __init__(self):
        self.capturer = Capturer(Section(100, 100, 100, 100), 0)
        self.window = PreviewWindow(self.capturer.capture_screenshot(), self.save)
        self.schedule_next_update()
        self.window.mainloop()


    def schedule_next_update(self):
        self.window.after(100, self.update)


    def update(self):
        self.capturer.set_section(self.get_section())
        self.window.set_image(self.capturer.capture_screenshot())
        self.schedule_next_update()


    def get_section(self):
        """
        Converts left, top, width, height to a Section object.
        """

        return Section(*self.window.get_all_numbers())


    def save(self, name):
        self.capturer.capture_screenshot().save(
            Path(__file__).parent.parent / "reference_images" / f"{name}.png",
            "PNG"
        )
        self.window.destroy()



if __name__ == "__main__":
    ScreenshotPreview()