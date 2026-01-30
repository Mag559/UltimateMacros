from pathlib import Path
from time import sleep
import logging

import pyperclip
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import prompt
from os import system
from action_completer import ActionCompleter

from screen_match.capturer import Section
from screen_match.screen_match import ScreenMatch

completer = ActionCompleter()

goto_group = completer.group("goto")


@goto_group.action("wikamp")
def _goto_wikamp():
    print("Visiting wikamp!")


@goto_group.action("youtube")
def _goto_youtube():
    print("you")

import sys

import pynput
from time import sleep


# mouse = pynput.mouse.Controller()
py_keyboard = pynput.keyboard.Controller()
py_key = pynput.keyboard.Key

LOADING_PAGE_WAIT_TIME = 6
TYPING_WAIT_TIME = 0.03
BEFORE_TAB_WAIT_TIME = 1



def press_with_ctrl(key):
    with py_keyboard.pressed(py_key.ctrl):
        py_keyboard.press(key)


def input_string(string, typing_delay=TYPING_WAIT_TIME):
    for s in string:
        py_keyboard.press(s)
        py_keyboard.release(s)
        sleep(typing_delay)


def enter():
    sleep(BEFORE_TAB_WAIT_TIME)
    py_keyboard.press(py_key.enter)
    py_keyboard.release(py_key.enter)



def tab(i):
    for _ in range(i):
        py_keyboard.press(py_key.tab)
        py_keyboard.release(py_key.tab)
        sleep(TYPING_WAIT_TIME)







# session = PromptSession()
#
# while True:
#     prompt_result = session.prompt("> ", completer=completer, validator=completer.get_validator())
#     completer.run_action(prompt_result)

if __name__ == "__main__":
    logging.basicConfig(filename='myapp.log', level=logging.DEBUG)
    screen_match = ScreenMatch() \
        .load_reference_image(Path(__file__).parent / "reference_images" / "firefox_open.png") \
        .set_compared_section(Section(0, 0, 100, 100))

    system('start firefox')

    if not screen_match.wait_for_match():
        quit(1)

    pyperclip.copy("https://login.p.lodz.pl/login?service=https%3A%2F%2Fedu.p.lodz.pl%2Flogin%2Findex.php%3FauthCAS%3DCAS")
    press_with_ctrl("v")
    enter()

    screen_match \
        .load_reference_image(Path(__file__).parent / "reference_images" / "cas_open.png") \
        .set_compared_section(Section(450, 910, 100, 100))

    if not screen_match.wait_for_match():
        quit(1)

    py_keyboard.press(py_key.down)
    sleep(0.1)
    enter()
    sleep(0.1)
    enter()
