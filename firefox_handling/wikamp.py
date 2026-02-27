from collections.abc import Callable
from logging import getLogger
from os import system
from pathlib import Path
from time import sleep
from pynput.keyboard import Key as PyKey
import pyperclip

from base_macro import InputPresser
from screen_match import ScreenMatch, Section

CAS = "https://login.p.lodz.pl/login?service=https%3A%2F%2Fedu.p.lodz.pl%2Flogin%2Findex.php%3FauthCAS%3DCAS"
REFERENCE_IMAGES = Path(__file__).parent.parent / "reference_images"


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
        self.screen_match.set_compared_section(Section(570, 1020, 1000, 60))

        possible_match = self.screen_match.find_match(0.98)
        if not possible_match:
            self.logger.debug("Firefox isn't open, need to open a new window")
            self.open_firefox()
            return

        InputPresser.move_mouse((570 + possible_match[0], 1020 + possible_match[1]))
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
