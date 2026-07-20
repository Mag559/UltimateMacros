from pynput import keyboard as py_keyboard, mouse as py_mouse

from um.base_macro import InputType, KeyInput, MouseInput
from um.helper_classes import OrderedEmitter


class MockInputCollector(OrderedEmitter):
    def __init__(self):
        super().__init__()

    def tap(self, key: py_keyboard.Key | py_keyboard.KeyCode | None) -> None:
        self.press(key)
        self.release(key)

    def press(self, key: py_keyboard.Key | py_keyboard.KeyCode | None) -> bool | None:
        key_input: KeyInput = KeyInput(key)

        self._emit(InputType.KEY_PRESS, key_input)

        return None

    def release(self, key: py_keyboard.Key | py_keyboard.KeyCode | None) -> bool | None:
        key_input: KeyInput = KeyInput(key)

        self._emit(InputType.KEY_RELEASE, key_input)

        return None

    def click(self, x, y, button: py_mouse.Button, pressed: bool) -> None:
        mouse_input: MouseInput = MouseInput(x, y, button)

        self._emit(InputType.MOUSE_PRESS if pressed else InputType.MOUSE_RELEASE, mouse_input)

        return None

    def click_anywhere(self, button: py_mouse.Button) -> None:
        self.click(0, 0, button, True)
        self.click(0, 0, button, False)

    def _emit(self, input_type: InputType, input_object: KeyInput | MouseInput) -> None:
        super()._emit(input_type, input_object)
