from enum import Enum
from logging import getLogger
from pathlib import Path
from time import sleep
from pynput.keyboard import Controller as KeyboardController, Key as PyKey
from pynput.mouse import Controller as MouseController, Button as PyButton

from screen_match import ScreenMatch

py_keyboard_controller = KeyboardController()
py_mouse_controller = MouseController()


REFERENCE_IMAGES = Path(__file__).parent.parent / "reference_images"

class InterpreterMode(Enum):
    END_ON_FAIL = 0
    IGNORE_FAIL = 1


class Interpreter:
    """
    Keeps the file open for the whole duration
    """
    def __init__(self, file_path: Path, mode: InterpreterMode=InterpreterMode.END_ON_FAIL):
        self.logger = getLogger(__name__)
        self.screen_match: ScreenMatch | None = None

        self.logger.info(f"Interpreting file {file_path}")
        with open(file_path, "r") as file:
            for line in file:
                try:
                    self.logger.debug(f"interpreting: {line}")
                    self.interpret(line)
                except KeyboardController.InvalidKeyException:
                    if mode == InterpreterMode.END_ON_FAIL:
                        self.logger.exception(f"Ending interpreter session after failing to interpret: {line}")
                        return
                    else:
                        self.logger.exception(f"Skipping instruction after failing to interpret: {line}")


    def interpret(self, line: str):
        items = line.split(" ")
        delay = items[0]
        if delay.isdecimal():
            sleep(float(delay))
            items.pop(0)

        instruction = items[0]
        match instruction:
            case "press":
                py_keyboard_controller.press(items[1])
            case "release":
                py_keyboard_controller.release(items[1])
            case "tap":
                py_keyboard_controller.press(items[1])
                sleep(float(items[2]))
                py_keyboard_controller.release(items[1])
            case "move":
                py_mouse_controller.move(
                    int(items[1].split(",")[0]) - py_mouse_controller.position[0],
                    int(items[1].split(",")[1]) - py_mouse_controller.position[1]
                )
            case "shift":
                py_mouse_controller.move(
                    int(items[1].split(",")[0]),
                    int(items[1].split(",")[1])
                )
            case "click":
                py_mouse_controller.press(PyButton(int(items[1])))
            case "await":
                if self.screen_match is None:
                    self.screen_match = ScreenMatch()
                    self.screen_match.load_reference_image(REFERENCE_IMAGES / items[1])
