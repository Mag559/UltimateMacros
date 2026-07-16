from argparse import ArgumentParser
from collections.abc import Callable
from enum import Enum

from pynput.keyboard import Key as PyKey, KeyCode
from pynput.mouse import Button as PyButton

from um.repeater.instruction_declarations import create_parsers
from um.repeater.registered_functions import create_function_registry


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

    parsers: dict[str, ArgumentParser] = create_parsers()
    registered_functions: dict[str, Callable] = create_function_registry()

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
