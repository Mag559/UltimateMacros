from collections.abc import Callable
from os import system
from pathlib import Path
from time import sleep
from pynput.keyboard import Key as PyKey
import pyperclip

from base_macro import InputPresser
from screen_match import ScreenMatch

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
        self.screen_match = ScreenMatch()
        self.open_firefox()

    def open_firefox(self):
        self.screen_match.load_reference_image(REFERENCE_IMAGES / "firefox_open.png")

        system('start firefox')
        if not self.screen_match.wait_for_match():
            self.on_fail()


    def open_website(self, url: str):
        InputPresser.tap_with_ctrl('e')
        InputPresser.tap(PyKey.backspace)
        pyperclip.copy(url)
        InputPresser.paste()
        InputPresser.enter()


    def open_wikamp(self):
        self.open_website(CAS)

        self.screen_match.load_reference_image(REFERENCE_IMAGES / "cas_open.png")

        if not self.screen_match.wait_for_match():
            self.on_fail()

        sleep(0.1)
        InputPresser.tap(PyKey.down)
        InputPresser.enter(1)
        InputPresser.enter(1)

        self.screen_match.load_reference_image(REFERENCE_IMAGES / "wikamp_open.png")
        if not self.screen_match.wait_for_match():
            self.on_fail()
