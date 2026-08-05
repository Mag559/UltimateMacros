from time import sleep

from pynput.keyboard import Controller as KeyboardController, Key as PyKey
from pynput.mouse import Controller as MouseController, Button as PyButton

from um.profiles import ProfileReader


class InputPresser:
    """
    Convenient wrapper for pynput keyboard and mouse input.

    Features sleep time arguments since they often need pauses around them,
    unfortunately coded manually for every function, so type checkers and other tooling don't get confused about
    the number of arguments.
    """

    py_keyboard_controller = KeyboardController()
    py_mouse_controller = MouseController()

    @staticmethod
    def paste(wait_before: float = 0) -> None:
        """
        Press ctrl + v
        :param wait_before: time to sleep before the input in seconds
        :return:
        """
        InputPresser.tap_with_ctrl('v', wait_before)

    @staticmethod
    def copy(wait_before: float = 0):
        """
        Press ctrl + c
        :param wait_before: time to sleep before the input in seconds
        :return:
        """
        InputPresser.tap_with_ctrl('c', wait_before)

    @staticmethod
    def tap_with_ctrl(
            key,
            wait_before: float = ProfileReader.profile().input_typing_wait_time,
            wait_mid: float = ProfileReader.profile().input_typing_wait_time,
    ) -> None:
        """
        Tap a key while the left control key is pressed.
        :param key: key to press with control
        :param wait_before: time to sleep before the input in seconds
        :param wait_mid: time to sleep between the individual events within the sequence
        :return:
        """
        sleep(wait_before)
        InputPresser.py_keyboard_controller.press(PyKey.ctrl_l)
        InputPresser.tap(key, wait_mid)
        sleep(wait_mid)
        InputPresser.py_keyboard_controller.release(PyKey.ctrl_l)

    @staticmethod
    def enter(wait_before: float = ProfileReader.profile().input_delay_before_enter) -> None:
        """
        Press enter
        :param wait_before: time to sleep before the input in seconds
        :return:
        """
        sleep(wait_before)
        InputPresser.py_keyboard_controller.tap(PyKey.enter)

    @staticmethod
    def press(key, wait_before: float = ProfileReader.profile().input_delay_before_enter) -> None:
        """
        Press the key and don't release it
        :param key: key to press
        :param wait_before: time to sleep before the input in seconds
        :return:
        """
        sleep(wait_before)
        InputPresser.py_keyboard_controller.press(key)

    @staticmethod
    def release(key, wait_before: float = ProfileReader.profile().input_delay_before_enter) -> None:
        """
        Release the key.
        :param key: key to release
        :param wait_before: time to sleep before the input in seconds
        :return:
        """
        sleep(wait_before)
        InputPresser.py_keyboard_controller.release(key)

    @staticmethod
    def tap(key, wait_before: float = ProfileReader.profile().input_typing_wait_time) -> None:
        """
        Press and release the key within a very short time window.
        :param key: the key to tap
        :param wait_before: time to sleep before the input in seconds
        :return:
        """
        sleep(wait_before)
        InputPresser.py_keyboard_controller.tap(key)

    @staticmethod
    def tab(count: int = 1, wait_time: float = ProfileReader.profile().input_delay_between_tabs) -> None:
        """
        Press and release tab repeatedly (intended for navigating menus)
        :param count: how many times
        :param wait_time: time to sleep before each tab press in seconds
        :return:
        """
        for _ in range(count):
            sleep(wait_time)
            InputPresser.py_keyboard_controller.tap(PyKey.tab)

    @staticmethod
    def type(string: str, typing_delay: float = ProfileReader.profile().input_typing_wait_time) -> None:
        """
        Press and release keys to type individual characters within the string,
        also works for characters normally requiring shift like `!` without the shift press and releasing
        :param string: string to type
        :param typing_delay: time to sleep between typing the characters in seconds
        :return:
        """
        for s in string:
            sleep(typing_delay)
            InputPresser.py_keyboard_controller.tap(s)

    @staticmethod
    def left_click(count: int = 1) -> None:
        """
        Click and release the left mouse button repeatedly in the current mouse position.
        :param count: how many times
        :return:
        """
        InputPresser.click_mouse(PyButton.left, count)

    @staticmethod
    def click_mouse(button: PyButton, count: int = 1) -> None:
        """
        Click and release a mouse button repeatedly in the current mouse position.
        :param button: which mouse button to use
        :param count: how many times
        :return:
        """
        InputPresser.py_mouse_controller.click(button, count=count)

    @staticmethod
    def move_mouse(to: tuple[int, int]) -> None:
        """
        Move the mouse to the given coordinates.
        :param to: absolute coordinates to move to
        :return:
        """
        InputPresser.py_mouse_controller.move(
            to[0] - InputPresser.py_mouse_controller.position[0],
            to[1] - InputPresser.py_mouse_controller.position[1]
        )

    @staticmethod
    def shift_mouse(by: tuple[int, int]) -> None:
        """
        Shift the mouse by the given offset.
        :param by: how much to move relative to the current position
        :return:
        """
        InputPresser.py_mouse_controller.move(
            by[0],
            by[1]
        )

    @staticmethod
    def scroll(by_x: int, by_y: int) -> None:
        """
        Emit a scroll signal, vertical, horizontal or both.
        :param by_x: how much to scroll horizontally
        :param by_y: how much to scroll vertically
        :return:
        """
        InputPresser.py_mouse_controller.scroll(by_x, by_y)
