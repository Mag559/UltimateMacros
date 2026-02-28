from collections.abc import Generator
from enum import Enum
from logging import getLogger
from pathlib import Path
from time import sleep
from pynput.keyboard import Controller as KeyboardController, Key as PyKey, KeyCode
from pynput.mouse import Controller as MouseController, Button as PyButton

from screen_match import ScreenMatch, REFERENCE_IMAGES

py_keyboard_controller = KeyboardController()
py_mouse_controller = MouseController()


class InterpreterMode(Enum):
    END_ON_FAIL = 0
    IGNORE_FAIL = 1


def build_file_interpreter(file_path: Path, mode: InterpreterMode=InterpreterMode.END_ON_FAIL):
    Interpreter(_read_file(file_path), mode)


def _read_file(file_path: Path):
    with open(file_path, "r") as file:
        for line in file:
            yield line



class Interpreter:
    """
    Execute instructions given by the instruction generator
    in the format specified in the readme
    """
    def __init__(self, instruction_generator: Generator, mode: InterpreterMode=InterpreterMode.END_ON_FAIL):
        self.logger = getLogger(__name__)
        self.screen_match: ScreenMatch | None = None
        self.instruction_generator = instruction_generator
        self.mode = mode


    def start(self):
        for line in self.instruction_generator:
            line = line.rstrip('\n')
            try:
                self.logger.debug(f"interpreting: {line}")
                self.interpret(line)
            except KeyboardController.InvalidKeyException:
                if self.mode == InterpreterMode.END_ON_FAIL:
                    self.logger.exception(f"Ending interpreter session after failing to interpret: {line}")
                    return
                else:
                    self.logger.exception(f"Skipping instruction after failing to interpret: {line}")

        self.logger.debug(f"Finished interpreting")


    @staticmethod
    def string_to_key(s: str):
        try:
            return PyKey[s]  # special key
        except KeyError:
            return KeyCode.from_char(s)  # regular character


    def interpret(self, line: str):
        if line.startswith("---"):
            return

        items = line.split(" ")
        try:
            sleep(float(items[0]))
            items.pop(0)
        except ValueError:
            pass

        instruction = items[0]
        match instruction:
            case "press":
                py_keyboard_controller.press(Interpreter.string_to_key(items[1]))
            case "release":
                py_keyboard_controller.release(Interpreter.string_to_key(items[1]))
            case "tap":
                py_keyboard_controller.press(Interpreter.string_to_key(items[1]))
                sleep(float(items[2]))
                py_keyboard_controller.release(Interpreter.string_to_key(items[1]))
            case "move":
                to_x = int(items[1].split(",")[0]) - py_mouse_controller.position[0]
                to_y = int(items[1].split(",")[1]) - py_mouse_controller.position[1]
                self.logger.debug(f"Moving mouse by: {to_x}, {to_y}")
                py_mouse_controller.move(to_x, to_y)
            case "shift":
                py_mouse_controller.move(
                    int(items[1].split(",")[0]),
                    int(items[1].split(",")[1])
                )
            case "click":
                py_mouse_controller.press(PyButton[items[1]])
                py_mouse_controller.release(PyButton[items[1]])
            case "await":
                if self.screen_match is None:
                    self.screen_match = ScreenMatch()
                    self.screen_match.load_reference_image(REFERENCE_IMAGES / items[1])
