import re
from collections.abc import Generator
from logging import getLogger
from time import time

from pynput import keyboard as py_keyboard
from queue import Queue

from um.base_macro import InputCollector, KeyInput, MouseInput, InputType
from um.helper_classes import OrderedEmitter
from um.profiles import ProfileReader


class Recorder:
    """
    Stores inputs received from the collector into a queue
    The main thread (running starts) processes them and yields the event as string
    """

    def __init__(self, collector: OrderedEmitter = InputCollector()):
        self.logger = getLogger(__name__)

        self._stop_flag: bool = False
        self._event_queue: Queue[str] = Queue()
        self._last_event_time: float = 0
        self.collector: OrderedEmitter = collector

        self.collector.add_caller(self._update, ProfileReader.profile().macro_recorder_priority)

    def start(self) -> Generator[str, None, None]:
        """
        Start keyboard and mouse event collection

        Acts as a generator method, returning recorded instructions
        """
        self.logger.debug(f"Start recording")

        while True:
            event: str = self._event_queue.get()
            self.logger.debug(f"Handling event: {event}")
            if self._stop_flag:
                self.logger.debug(f"Stop flag raised, ending the generator method")
                return

            timestamp, _, instruction = event.partition(" ")
            if self._last_event_time == 0:
                self._last_event_time = float(timestamp)

            event = f"{(float(timestamp) - self._last_event_time):.{
                ProfileReader.profile().macro_recorder_time_precision}f} {instruction}"
            self._last_event_time = float(timestamp)
            self.logger.debug(f"Event processed into: {event}")
            yield event

    def _update(self, input_type: InputType, input_object: KeyInput | MouseInput) -> None:
        self.logger.debug(f"Received {input_type} with input object {input_object}")
        match input_type:
            case InputType.KEY_PRESS:
                assert isinstance(input_object, KeyInput)
                self._on_key_press(input_object)
            case InputType.KEY_RELEASE:
                assert isinstance(input_object, KeyInput)
                self._on_key_release(input_object)
            case InputType.MOUSE_PRESS:
                assert isinstance(input_object, MouseInput)
                self._on_mouse_press(input_object)

    @staticmethod
    def key_to_string(key: py_keyboard.Key | py_keyboard.KeyCode | None) -> str | None:
        if re.search("^'\\\\x\\d\\d'$", str(key)):
            code = int(str(key)[-3:-1], 16)
            return chr(64 + code)

        if isinstance(key, py_keyboard.Key):
            return key.name
        elif isinstance(key, py_keyboard.KeyCode):
            return key.char
        elif isinstance(key, str):
            return key
        return None

    def _on_key_press(self, key_input: KeyInput) -> None:
        self._event_queue.put(f"{time()} press {Recorder.key_to_string(key_input.key)}")
        return None

    def _on_key_release(self, key_input: KeyInput):
        self._event_queue.put(f"{time()} release {Recorder.key_to_string(key_input.key)}")
        return None

    def _on_mouse_press(self, mouse_input: MouseInput):
        self._event_queue.put(f"{time()} move {mouse_input.x},{mouse_input.y}")
        self._event_queue.put(f"{time()} click {mouse_input.button.name}")
        return None

    def stop(self):
        self.logger.debug(f"Stop recording")
        self.collector.remove_caller(self._update)
        self._stop_flag = True
        self._event_queue.put("")
