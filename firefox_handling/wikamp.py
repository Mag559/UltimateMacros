from collections.abc import Callable
from os import system
from pathlib import Path
from time import sleep

import pyperclip

from base_macro.input_presser import InputPresser
from screen_match.capturer import Section
from screen_match.screen_match import ScreenMatch

CAS = "https://login.p.lodz.pl/login?service=https%3A%2F%2Fedu.p.lodz.pl%2Flogin%2Findex.php%3FauthCAS%3DCAS"


class FirefoxHandler:
    """
    Class handling a firefox window

    Executes `on_fail` Callable whenever a step goes wrong,
    usually quiting the program or retrying
    """
    def __init__(self, on_fail: Callable[[], None] = lambda _: None):
        self.on_fail = on_fail
        self.screen_match = ScreenMatch()
        self.open_firefox()

    def open_firefox(self):
        self.screen_match \
            .load_reference_image(Path(__file__).parent.parent / "reference_images" / "firefox_open.png") \
            .set_compared_section(Section(0, 0, 100, 100))

        system('start firefox')
        if not self.screen_match.wait_for_match():
            self.on_fail()


    def open_website(self, url: str):
        raise NotImplemented

    def open_cas(self):
        pyperclip.copy(CAS)
        InputPresser.paste()
        InputPresser.enter()

        self.screen_match \
            .load_reference_image(Path(__file__).parent / "reference_images" / "cas_open.png") \
            .set_compared_section(Section(450, 910, 100, 100))

        if not self.screen_match.wait_for_match():
            self.on_fail()

        InputPresser.tap('down')
        sleep(0.1)
        InputPresser.enter()
        sleep(0.1)
        InputPresser.enter()
