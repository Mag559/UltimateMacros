from time import sleep, time
from pynput import keyboard as py_keyboard, mouse as py_mouse
from enum import Enum
from logging import getLogger

from um.profiles import ProfileReader
from .signal_interfaces import Emitter


py_key = py_keyboard.Key


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


class MacroEventCollector(Emitter):
    """
    Collects input events listed in ImportantEvents.
    Upon collecting one, emits a signal

    Does detect inputs produced by InputPresser
    """
    def __init__(self):
        self.logger = getLogger(__name__)
        super().__init__()
        self.ctrl_held = False
        self.left_alt_held = False

        self.keyboard_listener: py_keyboard.Listener | None = None
        self.mouse_listener: py_mouse.Listener | None = None

        self.last_left_click: float = 0.0


    def start(self) -> None:
        # Collect events until released
        """
        Start keyboard and mouse event collection
        Does stop further code execution
        """
        self.keyboard_listener = py_keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release,
            name="InputCollector keyboard Listener"
        )

        self.mouse_listener = py_mouse.Listener(
            on_click=self.on_click,
            name="InputCollector mouse Listener"
        )

        self.logger.debug("listener threads started")
        self.keyboard_listener.start()
        self.mouse_listener.start()

        self.keyboard_listener.join()
        self.mouse_listener.join()


    def on_press(self, key):
        """
        Handle a keyboard key press, update modifier state, and emit matching ImportantEvents.
        
        Updates internal modifier flags when control or left-alt keys are pressed, emits:
        - SHORTCUT1 when left Alt is held and the '`' key is pressed,
        - COPY, PASTE, or CUT when the corresponding control-character key codes are received.
        Ignores non-character keys and returns False to stop the listener if termination was requested.
        
        Parameters:
            key: The pynput keyboard key object representing the pressed key.
        
        Returns:
            False if the collector has been marked for termination and the listener should stop, None otherwise.
        """
        try:
            self.logger.debug(f"Key pressed: {key}, as string: {str(key)}, as char: {key.char}")
        except AttributeError:
            self.logger.debug(f"Key pressed: {key}, as string: {str(key)}")
        match str(key):
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


    def on_release(self, key):
        """
        Handle a key release event by updating modifier state and optionally stopping collection.
        
        Parameters:
            key: The released key (e.g., a `pynput.keyboard.Key` or `pynput.keyboard.KeyCode`) whose release is being processed.
        
        Returns:
            False if the collector has been marked for termination and the listener should stop, None otherwise.
        """
        try:
            self.logger.debug(f"Key released: {key}, as string: {str(key)}, as char: {key.char}")
        except AttributeError:
            self.logger.debug(f"Key released: {key}, as string: {str(key)}")

        match key:
            case py_key.ctrl:
                self.ctrl_held = False
            case py_key.alt_l:
                self.left_alt_held = False
        return None


    def on_click(self, _x, _y, button, pressed):
        self.logger.debug('{0} {1}'.format(
                'Pressed' if pressed else 'Released',
                button))

        if not pressed:
            return None

        if button == py_mouse.Button.left:
            if time() - self.last_left_click < ProfileReader.profile().input_double_click_time:
                self.emit_event(ImportantEvents.DOUBLE_CLICK)
                self.last_left_click = 0
            else:
                self.last_left_click = time()

        if button == py_mouse.Button.right:
            self.emit_event(ImportantEvents.RIGHT_CLICK)

        return None



    def emit_event(self, event: ImportantEvents) -> None:
        """
        Emit the given ImportantEvents value to subscribed listeners.
        
        Delays for 0.15 seconds before calling the emitter to allow input handling to settle.
        
        Parameters:
            event (ImportantEvents): The event to emit to listeners.
        """
        self.logger.debug(f"Emitting event: {event}")
        sleep(ProfileReader.profile().input_event_emission_delay)
        self.emit(event)


    def stop(self):
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        self.logger.debug("listener threads stopped")
