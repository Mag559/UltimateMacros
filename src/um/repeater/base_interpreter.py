from argparse import ArgumentParser
from enum import Enum
from pathlib import Path

MACRO_FILES = Path(__file__).parents[3] / "macro_files"


class ThrowingArgumentParser(ArgumentParser):
    """
    Slightly modified version of the ArgumentParser from argparse,
    which throws a custom exception when an instruction doesn't match syntax.
    """
    def error(self, message: str):
        """
        Override the default error handling
        :param message: message explaining the error
        :raises: BaseInterpreter.InvalidInstruction with the given message
        """
        raise BaseInterpreter.InvalidInstruction(message)


class BaseInterpreter:
    """
    Parent class of the regular Interpreter.
    Declares commonly used static methods and classes to avoid circular dependencies.
    """

    class InvalidInstruction(Exception):
        """
        Thrown when the instruction has invalid syntax
        """

    class Mode(Enum):
        END_ON_FAIL = 0
        IGNORE_FAIL = 1

    @staticmethod
    def string_to_key(s: str):
        """
        Convert a string to pynput keyboard key.
        Imports pynput here, not at the top of the script,
        to allow the `scripts/generate_docs.py` script to run without this dependency.
        :param s: string keyname
        :return: None if s was None, pynput.keyboard.Key or KeyCode otherwise
        """
        if s is None:
            return None
        from pynput.keyboard import Key as PyKey, KeyCode
        try:
            return PyKey[s]  # special key
        except KeyError:
            return KeyCode.from_char(s)  # regular character

    @staticmethod
    def string_to_button(s: str):
        """
        Convert a string to pynput mouse button.
        Imports pynput here, not at the top of the script,
        to allow the `scripts/generate_docs.py` script to run without this dependency.
        :param s: string name of mouse button: left, right, middle
        :return: pynput.mouse.Button
        """
        if s is None:
            return None
        from pynput.mouse import Button as PyButton
        try:
            return PyButton[s]
        except KeyError:
            raise BaseInterpreter.InvalidInstruction(f"Invalid mouse button {s}")
