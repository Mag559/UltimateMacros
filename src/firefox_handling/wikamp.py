from collections.abc import Callable
from logging import getLogger
from os import system
from time import sleep

from pynput.keyboard import Key as PyKey
import pyperclip

from src.profiles import ProfileReader
from src.base_macro import InputPresser
from src.screen_match import ScreenMatch, Section, REFERENCE_IMAGES

CAS = "https://login.p.lodz.pl/login?service=https%3A%2F%2Fedu.p.lodz.pl%2Flogin%2Findex.php%3FauthCAS%3DCAS"


class FirefoxHandler:
    """
    Class handling a firefox window

    Executes `on_fail` Callable whenever a step goes wrong,
    usually quiting the program or retrying
    """
    def __init__(self, on_fail: Callable[[], None] = lambda: None):
        self.on_fail = on_fail
        self.logger = getLogger(__name__)
        self.screen_match = ScreenMatch()

        self.use_firefox_if_open()


    def use_firefox_if_open(self):
        self.screen_match.load_reference_image(REFERENCE_IMAGES / "firefox_minimized.png")
        self.screen_match.set_compared_section(Section(*ProfileReader.profile().match_taskbar_section))

        possible_match = self.screen_match.find_match(
            ProfileReader.profile().match_firefox_icon_confidence
        )
        if not possible_match:
            self.logger.debug("Firefox isn't open, need to open a new window")
            self.open_firefox()
            return

        InputPresser.move_mouse(
            (ProfileReader.profile().match_taskbar_section[0] + possible_match[0],
             ProfileReader.profile().match_taskbar_section[1] + possible_match[1]
             )
        )
        InputPresser.left_click()
        self.logger.debug("Firefox already open, hijacking the window")
        InputPresser.tap_with_ctrl('t')


    def open_firefox(self):
        self.screen_match.load_reference_image(REFERENCE_IMAGES / "firefox_open.png")

        system('start firefox')
        if not self.screen_match.wait_for_match():
            self.logger.error("Firefox failed to open")
            self.on_fail()


    def open_website(self, url: str):
        InputPresser.tap_with_ctrl('e')
        InputPresser.tap(PyKey.backspace)
        pyperclip.copy(url)
        InputPresser.paste()
        InputPresser.enter()
        self.logger.debug(f"Visiting {url}")


    def open_wikamp(self):
        self.open_website(CAS)

        self.screen_match.load_reference_image(REFERENCE_IMAGES / "cas_open.png")

        if not self.screen_match.wait_for_match():
            self.logger.error("CAS failed to load")
            self.on_fail()

        InputPresser.tap(PyKey.down)
        InputPresser.enter(1)
        InputPresser.enter(1)

        self.screen_match.load_reference_image(REFERENCE_IMAGES / "wikamp_open.png")
        if not self.screen_match.wait_for_match():
            self.logger.error("wikamp failed to load")
            self.on_fail()


    def wait_for_firefox_loading_wheel(self):
        # it takes a moment to change from loaded to loading
        sleep(ProfileReader.profile().match_firefox_loading_wheel_delay)
        self.screen_match.load_reference_image(REFERENCE_IMAGES / "firefox_loading_website.png")
        if not self.screen_match.wait_for_match():
            self.logger.error("website loading failed")
            self.on_fail()


    def press_register_attendance(self):
        self.screen_match.load_reference_image(REFERENCE_IMAGES / "wikamp_attendance_button.png")
        reference_img_section = self.screen_match.capturer.section

        self.screen_match.set_compared_section(Section(*ProfileReader.profile().match_whole_screen))

        possible_match = self.screen_match.find_match(
            ProfileReader.profile().match_wikamp_attendance_confidence
        )

        if not possible_match:
            self.logger.error("No register attendance button found")
            self.on_fail()

        InputPresser.move_mouse(
            (reference_img_section.width // 2 + possible_match[0],
             reference_img_section.height // 2 + possible_match[1])
        )
        InputPresser.left_click()
        self.logger.debug("Clicking register attendance")
