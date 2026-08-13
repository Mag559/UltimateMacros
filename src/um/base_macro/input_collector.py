from dataclasses import dataclass
from enum import Enum
from logging import getLogger
from queue import Queue, ShutDown
from threading import Thread

from pynput import keyboard as py_keyboard, mouse as py_mouse

from um.helper_classes import OrderedEmitter, SingletonMeta, CALLBACK


class InputType(Enum):
    KEY_PRESS = 0
    KEY_RELEASE = 1
    MOUSE_PRESS = 2
    MOUSE_RELEASE = 3


@dataclass
class KeyInput:
    """
    Dataclass representing a key used in the input,
    whether it was pressed or released is conveyed by an InputType object.

    Wraps pynput.keyboard.Key abd pynput.keyboard.KeyCode
    """
    key: py_keyboard.Key | py_keyboard.KeyCode | None

    def log(self):
        try:
            return f"as object {self.key}, as string: {str(self.key)}, as char: {self.key.char}"
        except AttributeError:
            return f"as object {self.key}, as string: {str(self.key)}"


@dataclass
class MouseInput:
    """
    Dataclass representing a mouse button and the location of the event,
    whether it was a click or a release is conveyed by an InputType object.

    Wraps pynput.mouse.Button
    """
    x: int
    y: int
    button: py_mouse.Button

    def log(self):
        return f"button {self.button} at ({self.x}, {self.y})"


class InputCollector(OrderedEmitter, metaclass=SingletonMeta):
    """
    Collects inputs from keyboard and mouse via pynput package
    and notifies observers about them in order of their priority.

    Being a Singleton it persists throughout the rest of the programs lifetime,
    however it stops it's threads if the last callback is removed and recreates them if a new one is added.

    Does detect inputs produced by InputPresser.

    Uses 3 threads:
    - keyboard listener
    - mouse listener
    - event consumer thread responsible for running callbacks with the events
    (to refrain from blocking the operating system's thread
    https://pynput.readthedocs.io/en/latest/mouse.html#monitoring-the-mouse)
    """

    def __init__(self):
        self.logger = getLogger(__name__)
        super().__init__()

        self.keyboard_listener: py_keyboard.Listener | None = None
        self.mouse_listener: py_mouse.Listener | None = None
        self._consumer: Thread | None = None
        self._event_queue: Queue[tuple[InputType, KeyInput | MouseInput]] | None = None

    def _create_consumer(self):
        """
        Create the consumer thread responsible for going through the event queue and emitting them.
        """
        self._consumer = Thread(target=self._consume_events, name="InputCollector consumer")
        self._event_queue = Queue()

    def add_callback(self, callback: CALLBACK, priority: int = 0) -> None:
        """
        Register a new priority callback like in the parent class,
        additionally recreate the threads if the newly added callback is the only one.

        Does not check if the threads are still alive and therefore with certain race conditions
        could recreate them before they have been stopped in ``InputCollector._stop()``

        :param callback: suited to handle ``input_type: InputType, input_object: KeyInput | MouseInput``
        :param priority: higher first
        """
        super().add_callback(callback, priority)
        if len(self._callers) == 1:
            self._run()

    def remove_callback(self, callback: CALLBACK) -> None:
        """
        Remove the callback like in the parent class,
        additionally stop the threads if there are no more callbacks registered.
        :param callback:
        :return:
        :raises ValueError: if callback is not registered
        """
        super().remove_callback(callback)
        if len(self._callers) == 0:
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

        self._create_consumer()

        self.logger.debug("listener threads started")
        self.keyboard_listener.start()
        self.mouse_listener.start()

        self._consumer.start()

    def _on_press(self, key: py_keyboard.Key | py_keyboard.KeyCode | None) -> bool | None:
        """
        Called by a pynput listener when a key is pressed.
        :param key: key that was pressed
        :return:
        """
        key_input: KeyInput = KeyInput(key)
        self.logger.debug(f"Key pressed: {key_input.log()}")

        self._emit(InputType.KEY_PRESS, key_input)

        return None

    def _on_release(self, key: py_keyboard.Key | py_keyboard.KeyCode | None) -> bool | None:
        """
        Called by a pynput listener when a key is released.
        :param key:
        :return:
        """
        key_input: KeyInput = KeyInput(key)
        self.logger.debug(f"Key released: {key_input.log()}")

        self._emit(InputType.KEY_RELEASE, key_input)

        return None

    def _on_click(self, x, y, button: py_mouse.Button, pressed: bool) -> None:
        """
        Called by pynput listener when a mouse button is pressed or released.
        :param x: x pixel coordinate
        :param y: y pixel coordinate
        :param button: which button was used
        :param pressed: true - pressed or false - released
        :return:
        """
        mouse_input: MouseInput = MouseInput(x, y, button)
        self.logger.debug(f'{'Pressed' if pressed else 'Released'} {mouse_input.log()}')

        self._emit(InputType.MOUSE_PRESS if pressed else InputType.MOUSE_RELEASE, mouse_input)

        return None

    def _emit(self, input_type: InputType, input_object: KeyInput | MouseInput) -> None:
        """
        Put the event in the queue to be handled by another thread.
        :param input_type: was a key pressed, key released, mouse pressed or mouse released
        :param input_object: details on which key / button was used
        :return:
        """
        self._event_queue.put((input_type, input_object))

    def _consume_events(self) -> None:
        """
        Consumer thread loop,
        picks up events from the queue and sends them to the parent class to be emitted.
        :return:
        """
        try:
            while not self._event_queue.is_shutdown:
                super()._emit(*self._event_queue.get())
        except ShutDown:
            pass
        self.logger.debug("Consumer thread run out of events to consume")

    def _stop(self):
        """
        (Temporarily) stop the threads.
        :return:
        """
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        self.logger.debug("listener threads stopped")
        self._event_queue.shutdown()
