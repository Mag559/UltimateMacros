from time import time

from pynput import keyboard as py_keyboard, mouse as py_mouse
from queue import Queue


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


    def record(self):
        """
        Start keyboard and mouse event collection
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

        while True:
            event = self.event_queue.get()
            # assert event is str
            timestamp, _, instruction = event.partition(" ")
            if self.last_event_time == 0:
                self.last_event_time = float(timestamp)

            event = f"{(float(timestamp) - self.last_event_time):.3f} {instruction}"
            self.last_event_time = float(timestamp)
            yield event

    @staticmethod
    def key_to_string(key):
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
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
