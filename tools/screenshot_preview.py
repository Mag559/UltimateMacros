from pathlib import Path
from preview_window import PreviewWindow
from screen_match.capturer import Capturer


class ScreenshotPreview:
    def __init__(self):
        self.capturer = Capturer((0, 0, 1920, 1080), 0)
        self.window = PreviewWindow(self.capturer.capture_screenshot(), self.save)
        self.schedule_next_update()
        self.window.mainloop()


    def schedule_next_update(self):
        self.window.after(100, self.update)


    def update(self):
        self.capturer.section = self.get_section()
        self.window.set_image(self.capturer.capture_screenshot())
        self.schedule_next_update()


    def get_section(self):
        """
        Converts left, top, width, height supplied by the window input
        to left, top, right, bottom required by PIL crop
        """
        v = self.window.get_all_numbers()
        return v[0], v[1], v[0] + v[2], v[1] + v[3]


    def save(self, name):
        self.capturer.capture_screenshot().save(
            Path(__file__).parent.parent / "reference_images" / f"{name}.png",
            "PNG"
        )
        self.window.destroy()



if __name__ == "__main__":
    ScreenshotPreview()