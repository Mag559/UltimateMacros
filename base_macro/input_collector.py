from time import sleep, time
from pynput import keyboard as py_keyboard, mouse as py_mouse
from enum import Enum

from .signal_interfaces import Emitter


py_key = py_keyboard.Key

DOUBLE_CLICK_TIME = 0.2


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


class InputCollector(Emitter):
    """
    Collects input events listed in ImportantEvents.
    Upon collecting one, emits a signal

    Does detect inputs produced by InputPresser
    """
    def __init__(self, debug_mode=False):
        super().__init__()
        self.ctrl_held = False
        self.left_alt_held = False

        self.debug_mode = debug_mode

        self.keyboard_listener: py_keyboard.Listener | None = None
        self.mouse_listener: py_mouse.Listener | None = None

        self.last_left_click: float = 0.0


    def start(self) -> None:
        # Collect events until released
        """
        Start keyboard and mouse event collection
        Does not stop further code execution, see join for that
        """
        self.keyboard_listener = py_keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release,
        )

        self.mouse_listener = py_mouse.Listener(
                on_click=self.on_click
        )

        self.keyboard_listener.start()
        self.mouse_listener.start()


    def join(self):
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
            if self.debug_mode:
                print(f"Key pressed: {key}, as string: {str(key)}, as char: {key.char}")
        except AttributeError:
            print(f"Key pressed: {key}, as string: {str(key)}")
        match str(key):
            case "Key.ctrl_l":
                if self.debug_mode:
                    print("ctrl_held")
                self.ctrl_held = True
            case "Key.ctrl_r":
                if self.debug_mode:
                    print("ctrl_held")
                self.ctrl_held = True
            case "Key.alt_l":
                if self.debug_mode:
                    print("left_alt_held")
                self.left_alt_held = True
            case "'`'":
                if self.left_alt_held:
                    self.emit_event(ImportantEvents.SHORTCUT1)
            case "'\\x03'":
                print(key)
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
            if self.debug_mode:
                print(f"Key released: {key}, as string: {str(key)}, as char: {key.char}")
        except AttributeError:
            print(f"Key released: {key}, as string: {str(key)}")

        match key:
            case py_key.ctrl:
                self.ctrl_held = False
            case py_key.alt_l:
                self.left_alt_held = False
        return None


    def on_click(self, _x, _y, button, pressed):
        if self.debug_mode:
            print('{0} {1}'.format(
                'Pressed' if pressed else 'Released',
                button))

        if not pressed:
            return None

        if button == py_mouse.Button.left:
            if time() - self.last_left_click < DOUBLE_CLICK_TIME:
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
        
        Delays for 0.1 seconds before calling the emitter to allow input handling to settle. When debug_mode is enabled, prints the event to stdout.
        
        Parameters:
            event (ImportantEvents): The event to emit to listeners.
        """
        if self.debug_mode:
            print(f"event: {event}")
        sleep(0.15)
        self.emit(event)


    def stop(self):
        self.keyboard_listener.stop()
        self.mouse_listener.stop()



# broken
# class SelfIgnoringInputCollector(InputCollector):
#     """
#     Compared to the normal input collector, ignores self produced events
#     """
#     def __init__.py(self, debug_mode=False):
#         """
#         Initialize the SelfIgnoringInputCollector and enable tracking of events it generates.
#
#         Parameters:
#             debug_mode (bool): If True, enable verbose debugging output for input handling.
#
#         Detailed behavior:
#             The instance starts with `produced_event` set to `False`; set to `True` when this collector simulates an input so the subsequent emitted event can be identified and ignored.
#         """
#         super().__init__.py(debug_mode)
#         self.produced_event = False
#
#
#     def paste(self):
#         """
#         Mark the next event as self-produced and simulate a system paste operation.
#
#         This sets the collector's internal flag indicating the following emitted event was generated by this instance, then invokes the platform paste action.
#         """
#         self.produced_event = True
#         if self.debug_mode:
#             print("Pasting, ignoring")
#         sleep(0.1)
#         InputPresser.paste()
#
#
#     @override
#     def emit_event(self, event: ImportantEvents) -> None:
#         """
#         Emit an ImportantEvents event unless the collector marked it as self-produced.
#
#         If this collector's produced_event flag is set, the method clears that flag and does not propagate the event. Otherwise, the event is emitted via the base Emitter implementation.
#
#         Parameters:
#             event (ImportantEvents): The event to emit.
#         """
#         if self.produced_event:
#             if self.debug_mode:
#                 print(f"ignored self produced event: {event}")
#             self.produced_event = False
#             return
#         super().emit_event(event)