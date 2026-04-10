from time import sleep

from pynput.keyboard import Controller as KeyboardController, Key as PyKey
from pynput.mouse import Controller as MouseController, Button as PyButton

from um.profiles import ProfileReader

py_keyboard_controller = KeyboardController()
py_mouse_controller = MouseController()


def delay(func):
    def wrapper(*args, **kwargs):
        sleep(ProfileReader.profile().input_typing_wait_time)
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
        # noinspection PyTypeChecker
        with py_keyboard_controller.pressed(PyKey.ctrl):
            py_keyboard_controller.tap(key)

    @staticmethod
    def enter(wait_before: float = ProfileReader.profile().input_delay_before_enter):
        sleep(wait_before)
        py_keyboard_controller.tap(PyKey.enter)

    @staticmethod
    @delay
    def tap(key):
        py_keyboard_controller.tap(key)


    @staticmethod
    def tab(count: int = 1, wait_time: float = ProfileReader.profile().input_delay_between_tabs):
        for _ in range(count):
            py_keyboard_controller.tap(PyKey.tab)
            sleep(wait_time)


    @staticmethod
    def input_string(string: str, typing_delay: float= ProfileReader.profile().input_typing_wait_time):
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


    @staticmethod
    def scroll(by: int):
        py_mouse_controller.scroll(0, by)