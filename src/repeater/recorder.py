import re
from logging import getLogger
from time import time

from pynput import keyboard as py_keyboard, mouse as py_mouse
from queue import Queue

from src.profiles import ProfileReader


class Recorder:
    """
    Individual threads record timestamps into the instructions
    Which are converted to delays by a single consumer that returns them
    """
    def __init__(self):
        self.keyboard_listener: py_keyboard.Listener | None = None
        self.mouse_listener: py_mouse.Listener | None = None
        self.stop_flag : bool = False
        self.event_queue: Queue = Queue()
        self.last_event_time: float = 0

        self.logger = getLogger(__name__)


    def start(self):
        """
        Start keyboard and mouse event collection

        Acts as a generator method, returning recorded instructions
        """
        self.keyboard_listener = py_keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )

        self.mouse_listener = py_mouse.Listener(
            on_click=self._on_click
        )

        self.keyboard_listener.start()
        self.mouse_listener.start()

        self.logger.debug(f"Start recording")

        while True:
            event = self.event_queue.get()
            self.logger.debug(f"Handling event: {event}")
            if self.stop_flag:
                self.logger.debug(f"Stop flag raised, ending the generator method")
                return

            # assert event is str
            timestamp, _, instruction = event.partition(" ")
            if self.last_event_time == 0:
                self.last_event_time = float(timestamp)

            event = f"{(float(timestamp) - self.last_event_time) \
                :.{ProfileReader.profile().macro_recorder_time_precision}f} {instruction}"
            self.last_event_time = float(timestamp)
            self.logger.debug(f"Event processed into: {event}")
            yield event


    @staticmethod
    def key_to_string(key):
        if re.search("^'\\\\x\\d\\d'$", str(key)):
            code = int(str(key)[-3:-1], 16)
            return chr(64 + code)

        if isinstance(key, py_keyboard.Key):
            return key.name
        elif isinstance(key, py_keyboard.KeyCode):
            return key.char
        return None


    def _on_press(self, key):
        self.event_queue.put(f"{time()} press {Recorder.key_to_string(key)}")
        return None

    def _on_release(self, key):
        self.event_queue.put(f"{time()} release {Recorder.key_to_string(key)}")
        return None

    def _on_click(self, x, y, button, pressed):
        if not pressed:
            return None
        self.event_queue.put(f"{time()} move {x},{y}")
        self.event_queue.put(f"{time()} click {button.name}")
        return None


    def stop(self):
        self.logger.debug(f"Stop recording")
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        self.stop_flag = True
        self.event_queue.put("")
