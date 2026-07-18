from time import sleep

from pynput.keyboard import Controller as KeyboardController, Key as PyKey
from pynput.mouse import Controller as MouseController, Button as PyButton

from um.profiles import ProfileReader


class InputPresser:
    """
    Convenient wrapper for pynput keyboard and mouse input
    includes delays for certain methods
    """

    py_keyboard_controller = KeyboardController()
    py_mouse_controller = MouseController()

    @staticmethod
    def paste(wait_before: float = 0):
        sleep(wait_before)
        InputPresser.tap_with_ctrl('v')

    @staticmethod
    def copy(wait_before: float = 0):
        sleep(wait_before)
        InputPresser.tap_with_ctrl('c')

    @staticmethod
    def tap_with_ctrl(
            key,
            wait_before: float = ProfileReader.profile().input_typing_wait_time,
            wait_mid: float = ProfileReader.profile().input_typing_wait_time,
    ):
        sleep(wait_before)
        InputPresser.py_keyboard_controller.press(PyKey.ctrl_l)
        InputPresser.tap(key, wait_mid)
        sleep(wait_mid)
        InputPresser.py_keyboard_controller.release(PyKey.ctrl_l)

    @staticmethod
    def enter(wait_before: float = ProfileReader.profile().input_delay_before_enter):
        sleep(wait_before)
        InputPresser.py_keyboard_controller.tap(PyKey.enter)

    @staticmethod
    def press(key, wait_before: float = ProfileReader.profile().input_delay_before_enter):
        sleep(wait_before)
        InputPresser.py_keyboard_controller.press(key)

    @staticmethod
    def release(key, wait_before: float = ProfileReader.profile().input_delay_before_enter):
        sleep(wait_before)
        InputPresser.py_keyboard_controller.release(key)

    @staticmethod
    def tap(key, wait_before: float = ProfileReader.profile().input_typing_wait_time):
        sleep(wait_before)
        InputPresser.py_keyboard_controller.tap(key)

    @staticmethod
    def tab(count: int = 1, wait_time: float = ProfileReader.profile().input_delay_between_tabs):
        for _ in range(count):
            sleep(wait_time)
            InputPresser.py_keyboard_controller.tap(PyKey.tab)

    @staticmethod
    def type(string: str, typing_delay: float = ProfileReader.profile().input_typing_wait_time):
        for s in string:
            sleep(typing_delay)
            InputPresser.py_keyboard_controller.tap(s)

    @staticmethod
    def left_click(count: int = 1):
        InputPresser.click_mouse(PyButton.left, count)

    @staticmethod
    def click_mouse(button: PyButton, count: int = 1):
        InputPresser.py_mouse_controller.click(button, count=count)

    @staticmethod
    def move_mouse(to: tuple[int, int]):
        InputPresser.py_mouse_controller.move(
            to[0] - InputPresser.py_mouse_controller.position[0],
            to[1] - InputPresser.py_mouse_controller.position[1]
        )

    @staticmethod
    def shift_mouse(by: tuple[int, int]):
        InputPresser.py_mouse_controller.move(
            by[0],
            by[1]
        )

    @staticmethod
    def scroll(by_x: int, by_y: int):
        InputPresser.py_mouse_controller.scroll(by_x, by_y)
