from time import time
from enum import Enum
from logging import getLogger

from um.profiles import ProfileReader
from .input_collector import InputCollector, KeyInput, MouseInput, InputType
from um.helper_classes import OrderedEmitter, CALLBACK
from pynput import keyboard as py_keyboard, mouse as py_mouse


class ImportantEvents(Enum):
    COPY = 1
    PASTE = 2
    CUT = 3
    SHORTCUT1 = 4 # left alt + `
    SHORTCUT2 = 9 # left alt + windows
    TOGGLE = 5
    DOUBLE_CLICK = 6
    RIGHT_CLICK = 7
    MIDDLE_CLICK = 8
    SAVE = 10


class MacroEventCollector(OrderedEmitter):
    """
    Filters out important events amongst inputs collected by input collector.
    """
    def __init__(self):
        self.logger = getLogger(__name__)
        super().__init__()
        self.ctrl_held = False
        self.left_alt_held = False

        self.last_left_click: float = 0.0

        InputCollector().add_caller(self._on_update, ProfileReader.profile().macro_event_collector_priority)


    def _on_update(self, input_type: InputType, input_object: KeyInput | MouseInput) -> None:
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
                self._on_mouse_pressed(input_object)


    def _on_key_press(self, key_input: KeyInput):
        """
        Handle a keyboard key press, update modifier state, and emit matching ImportantEvents.
        
        Updates internal modifier flags when control or left-alt keys are pressed, emits:
        - SHORTCUT1 when left Alt is held and the '`' key is pressed,
        - COPY, PASTE, or CUT when the corresponding control-character key codes are received.
        Ignores non-character keys and returns False to stop the listener if termination was requested.
        
        Parameters:
            key_input: KeyInput object representing the pressed key.
        
        Returns:
            False if the collector has been marked for termination and the listener should stop, None otherwise.
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
                    self.emit_event(ImportantEvents.SHORTCUT1)
            case "'\\x03'":
                self.emit_event(ImportantEvents.COPY)
            case "'\\x16'":
                self.emit_event(ImportantEvents.PASTE)
            case "'\\x18'":
                self.emit_event(ImportantEvents.CUT)
            case "'\\x13'":
                self.emit_event(ImportantEvents.SAVE)
            case "Key.num_lock":
                self.emit_event(ImportantEvents.TOGGLE)
            case "Key.cmd":
                if self.left_alt_held:
                    self.emit_event(ImportantEvents.SHORTCUT2)

        return None


    def _on_key_release(self, key_input: KeyInput):
        """
        Handle a key release event by updating modifier state
        
        Parameters:
            key_input: KeyInput object representing the pressed key.
        
        Returns:
            False if the collector has been marked for termination and the listener should stop, None otherwise.
        """
        match key_input.key:
            case py_keyboard.Key.ctrl:
                self.ctrl_held = False
            case py_keyboard.Key.alt_l:
                self.left_alt_held = False
        return None


    def _on_mouse_pressed(self, mouse_input: MouseInput):
        if mouse_input.button == py_mouse.Button.left:
            if time() - self.last_left_click < ProfileReader.profile().input_double_click_time:
                self.emit_event(ImportantEvents.DOUBLE_CLICK)
                self.last_left_click = 0
            else:
                self.last_left_click = time()

        if mouse_input.button == py_mouse.Button.right:
            self.emit_event(ImportantEvents.RIGHT_CLICK)

        return None


    def emit_event(self, event: ImportantEvents) -> None:
        self.logger.debug(f"Emitting event: {event}")
        self._emit(event)


    def remove_caller(self, callback: CALLBACK) -> None:
        """
        Remove caller, if it's the last one, disconnect from InputCollector Singleton
        """
        super().remove_caller(callback)
        if len(self._callers) == 0:
            InputCollector().remove_caller(self._on_update)
