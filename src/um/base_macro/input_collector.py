from dataclasses import dataclass
from enum import Enum
from time import sleep
from pynput import keyboard as py_keyboard, mouse as py_mouse
from logging import getLogger

from um.profiles import ProfileReader
from um.helper_classes import OrderedEmitter, SingletonMeta, CALLBACK


class InputType(Enum):
    KEY_PRESS = 0
    KEY_RELEASE = 1
    MOUSE_PRESS = 2
    MOUSE_RELEASE = 3


@dataclass
class KeyInput:
    key: py_keyboard.Key | py_keyboard.KeyCode | None
    def log(self):
        try:
            return f"as object {self.key}, as string: {str(self.key)}, as char: {self.key.char}"
        except AttributeError:
            return f"as object {self.key}, as string: {str(self.key)}"


@dataclass
class MouseInput:
    x: int
    y: int
    button: py_mouse.Button
    def log(self):
        return f"button {self.button} at ({self.x}, {self.y})"


class InputCollector(OrderedEmitter, metaclass=SingletonMeta):
    """
    Collects inputs from keyboard and mouse via pynput package
    and notifies observers about them in order of their priority

    Does detect inputs produced by InputPresser
    """
    def __init__(self):
        self.logger = getLogger(__name__)
        super().__init__()

        self.keyboard_listener: py_keyboard.Listener | None = None
        self.mouse_listener: py_mouse.Listener | None = None


    def add_caller(self, callback: CALLBACK, priority: int = 0) -> None:
        super().add_caller(callback, priority)
        if len(self._callers) == 1:
            self._run()


    def remove_caller(self, callback: CALLBACK) -> None:
        super().remove_caller(callback)
        if len(self._callers) == 1:
            self._stop()


    def _run(self) -> None:
        """
        Start keyboard and mouse event collection
        Does not stop further code execution
        """
        self.keyboard_listener = py_keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
            name="InputCollector keyboard Listener"
        )

        self.mouse_listener = py_mouse.Listener(
            on_click=self._on_click,
            name="InputCollector mouse Listener"
        )

        self.logger.debug("listener threads started")
        self.keyboard_listener.start()
        self.mouse_listener.start()


    def _on_press(self, key: py_keyboard.Key | py_keyboard.KeyCode | None) -> bool | None:
        key_input: KeyInput = KeyInput(key)
        self.logger.debug(f"Key pressed: {key_input.log()}")

        self._emit(InputType.KEY_PRESS, key_input)

        return None


    def _on_release(self, key: py_keyboard.Key | py_keyboard.KeyCode | None) -> bool | None:
        key_input: KeyInput = KeyInput(key)
        self.logger.debug(f"Key released: {key_input.log()}")

        self._emit(InputType.KEY_RELEASE, key_input)

        return None


    def _on_click(self, x, y, button: py_mouse.Button, pressed):
        mouse_input: MouseInput = MouseInput(x, y, button)
        self.logger.debug(f'{'Pressed' if pressed else 'Released'} {mouse_input.log()}')

        self._emit(InputType.MOUSE_PRESS if pressed else InputType.MOUSE_RELEASE, mouse_input)

        return None


    def _emit(self, input_type: InputType, input_object: KeyInput | MouseInput) -> None:
        # TODO: Delays for 0.15 seconds before calling the emitter to allow input handling to settle.

        sleep(ProfileReader.profile().input_event_emission_delay)
        super()._emit(input_type, input_object)


    def _stop(self):
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        self.logger.debug("listener threads stopped")

