from argparse import ArgumentParser
from enum import Enum

from pynput.keyboard import Key as PyKey, KeyCode
from pynput.mouse import Button as PyButton


class ThrowingArgumentParser(ArgumentParser):
    def error(self, message: str):
        raise BaseInterpreter.InvalidInstruction(message)


class BaseInterpreter:
    """
    Execute instructions given by the instruction generator
    in the format specified in the readme
    """

    class InvalidInstruction(Exception):
        """
        Thrown when the instruction doesn't have a parser or
        """

    class Mode(Enum):
        END_ON_FAIL = 0
        IGNORE_FAIL = 1

    @staticmethod
    def string_to_key(s: str):
        try:
            return PyKey[s]  # special key
        except KeyError:
            return KeyCode.from_char(s)  # regular character

    @staticmethod
    def string_to_button(s: str) -> PyButton:
        try:
            return PyButton[s]
        except KeyError:
            raise BaseInterpreter.InvalidInstruction(f"Invalid mouse button {s}")
