from pynput.keyboard import Controller, Key as py_key
py_keyboard_controller = Controller()

class InputPresser:
    @staticmethod
    def paste():
        with py_keyboard_controller.pressed(py_key.ctrl):
            py_keyboard_controller.press('v')
            py_keyboard_controller.release('v')