from time import sleep

from pynput.keyboard import Controller, Key as PyKey
py_keyboard_controller = Controller()

TYPING_WAIT_TIME = 0.03

class InputPresser:
    @staticmethod
    def paste():
        # py_keyboard_controller.release('c')
        InputPresser.press_with_ctrl('v')

    @staticmethod
    def press_with_ctrl(key):
        with py_keyboard_controller.pressed(PyKey.ctrl):
            py_keyboard_controller.tap(key)

    @staticmethod
    def enter(wait_before: float = 0.5):
        sleep(wait_before)
        py_keyboard_controller.tap(PyKey.enter)

    @staticmethod
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