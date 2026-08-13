from time import time
from enum import Enum
from logging import getLogger

from um.profiles import ProfileReader
from .input_collector import InputCollector, KeyInput, MouseInput, InputType
from um.helper_classes import OrderedEmitter, CALLBACK
from pynput import keyboard as py_keyboard, mouse as py_mouse


class ImportantEvent(Enum):
    COPY = 1
    PASTE = 2
    CUT = 3
    SHORTCUT1 = 4  # left alt + `
    SHORTCUT2 = 9  # left alt + windows
    TOGGLE = 5
    DOUBLE_CLICK = 6
    RIGHT_CLICK = 7
    MIDDLE_CLICK = 8
    SAVE = 10


class MacroEventCollector(OrderedEmitter):
    """
    Filters out important events amongst inputs collected by input collector
    and passes them out in the same fashion - via OrderedEmitter.
    """

    def __init__(self, collector: OrderedEmitter = None):
        """

        :param collector: source of the raw inputs, input collector Singleton by default
        """
        self.logger = getLogger(__name__)
        super().__init__()
        self.ctrl_held = False
        self.left_alt_held = False

        self.last_left_click: float = 0.0
        if collector is None:
            self.collector: OrderedEmitter = InputCollector()
        else:
            self.collector: OrderedEmitter = collector

    def run(self) -> None:
        """
        Connect to the raw input source and thus start emitting events.
        :return:
        """
        self.collector.add_callback(self._update, ProfileReader.profile().macro_event_collector_priority)

    def _update(self, input_type: InputType, input_object: KeyInput | MouseInput) -> None:
        """
        Method called by the raw input collector.
        Figures out what input event type it is and delegate the rest to another method.
        :param input_type: was the key pressed, released or mouse pressed, released
        :param input_object: what key or button was used
        :return:
        """
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

    def _on_key_press(self, key_input: KeyInput) -> bool | None:
        """
        Handle a keyboard key press by tracking which modifier (alt, ctrl) keys are held
        and emitting ImportantEvents

        :param key_input: KeyInput object representing the pressed key.
        :return:
        """
        match str(key_input.key):
            case "Key.ctrl_l":
                self.ctrl_held = True
            case "Key.ctrl_r":
                self.ctrl_held = True
            case "Key.alt_l":
                self.left_alt_held = True
            case "'`'":
                if self.left_alt_held:
                    self.emit_event(ImportantEvent.SHORTCUT1)
            case "'\\x03'":
                self.emit_event(ImportantEvent.COPY)
            case "'\\x16'":
                self.emit_event(ImportantEvent.PASTE)
            case "'\\x18'":
                self.emit_event(ImportantEvent.CUT)
            case "'\\x13'":
                self.emit_event(ImportantEvent.SAVE)
            case "Key.num_lock":
                self.emit_event(ImportantEvent.TOGGLE)
            case "Key.cmd":
                if self.left_alt_held:
                    self.emit_event(ImportantEvent.SHORTCUT2)

        return None

    def _on_key_release(self, key_input: KeyInput) -> bool | None:
        """
        Track which modifier keys were released.
        """
        match key_input.key:
            case py_keyboard.Key.ctrl:
                self.ctrl_held = False
            case py_keyboard.Key.alt_l:
                self.left_alt_held = False
        return None

    def _on_mouse_press(self, mouse_input: MouseInput) -> bool | None:
        """
        Handle the recorded event and emit mouse based ImportantEvents
        :param mouse_input: MouseInput object representing the pressed mouse button.
        :return:
        """
        if mouse_input.button == py_mouse.Button.left:
            if time() - self.last_left_click < ProfileReader.profile().input_double_click_time:
                self.emit_event(ImportantEvent.DOUBLE_CLICK)
                self.last_left_click = 0
            else:
                self.last_left_click = time()

        if mouse_input.button == py_mouse.Button.right:
            self.emit_event(ImportantEvent.RIGHT_CLICK)

        if mouse_input.button == py_mouse.Button.middle:
            self.emit_event(ImportantEvent.MIDDLE_CLICK)

        return None

    def emit_event(self, event: ImportantEvent) -> None:
        """
        Callback subscribers based on their priority about the event.
        :param event: ImportantEvents object representing the event.
        """
        self.logger.debug(f"Emitting event: {event}")
        self._emit(event)

    def remove_callback(self, callback: CALLBACK) -> None:
        """
        Remove caller,
        if it's the last one, disconnect from the InputCollector Singleton.
        :param callback: Callable to be removed
        :return:
        """
        super().remove_callback(callback)
        if len(self._callers) == 0:
            self.collector.remove_callback(self._update)
