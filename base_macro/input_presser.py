from time import sleep

from pynput.keyboard import Controller as KeyboardController, Key as PyKey
from pynput.mouse import Controller as MouseController, Button as PyButton


py_keyboard_controller = KeyboardController()
py_mouse_controller = MouseController()

TYPING_WAIT_TIME = 0.03

def delay(func):
    def wrapper(*args, **kwargs):
        sleep(TYPING_WAIT_TIME)
        return func(*args, **kwargs)
    return wrapper


class InputPresser:
    """
    Convenient wrapper for pynput keyboard and mouse input
    includes delays for certain methods
    """
    @staticmethod
    def paste():
        InputPresser.tap_with_ctrl('v')

    @staticmethod
    def copy():
        InputPresser.tap_with_ctrl('c')

    @staticmethod
    @delay
    def tap_with_ctrl(key):
        with py_keyboard_controller.pressed(PyKey.ctrl):
            py_keyboard_controller.tap(key)

    @staticmethod
    def enter(wait_before: float = 0.5):
        sleep(wait_before)
        py_keyboard_controller.tap(PyKey.enter)

    @staticmethod
    @delay
    def tap(key):
        py_keyboard_controller.tap(key)


    @staticmethod
    def tab(count: int = 1, wait_time: float = TYPING_WAIT_TIME):
        for _ in range(count):
            py_keyboard_controller.tap(PyKey.tab)
            sleep(wait_time)


    @staticmethod
    def input_string(string: str, typing_delay: float=TYPING_WAIT_TIME):
        for s in string:
            py_keyboard_controller.tap(s)
            sleep(typing_delay)


    @staticmethod
    def left_click(count: int = 1):
        py_mouse_controller.click(PyButton.left, count=count)


    @staticmethod
    def move_mouse(to: tuple[int, int]):
        py_mouse_controller.move(
            to[0] - py_mouse_controller.position[0],
            to[1] - py_mouse_controller.position[1]
        )