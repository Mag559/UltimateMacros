import shlex
from inspect import signature
from collections.abc import Generator, Callable
from logging import getLogger
from pathlib import Path
from time import sleep
from typing import Any

import pyperclip
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Button as PyButton

import um.base_macro
from um.profiles import ProfileReader, MACRO_FILES
import um.screen_match
from .base_interpreter import BaseInterpreter, ThrowingArgumentParser
from .instruction_declarations import create_parsers
from .registered_functions import create_function_registry


def build_file_interpreter(
    file_path: Path | str,
    mode: BaseInterpreter.Mode = BaseInterpreter.Mode(
        ProfileReader.profile().macro_interpreter_mode
    )
) -> Interpreter:
    """
    Create the simplest Interpreter variant, with instructions in the specified file.
    :param file_path: path to the text file with instructions, by convention with .ins extension,
    relative to `macro_files` in the project root directory
    :param mode: how should the interpreter react to an invalid instruction - end its work or skip the instruction
    :return: initialized, but not started Interpreter
    """
    return Interpreter(_read_file(MACRO_FILES / file_path), mode)


def _read_file(file_path: Path) -> Generator[str, None, None]:
    """
    Create a generator that yields lines from a text file.
    :param file_path: path to the text file,
    global or relative to the project root directory assuming it's the current directory when running
    :return: Generator object
    """
    with open(file_path, "r") as file:
        for line in file:
            yield line


def filter_nones(function: Callable, *args) -> Any:
    """
    Call the function with specified arguments while swapping any Nones out for default values
    :param function: function to call
    :param args: any number of arguments
    :returns: return value of the called function
    """
    argument_names = signature(function).parameters.keys()
    assert len(argument_names) >= len(args)
    
    arguments: dict[str, Any] = {}
    for name, arg in zip(argument_names, args):
        if arg is not None:
            arguments[name] = arg
    return function(**arguments)


class Interpreter(BaseInterpreter):
    """
    Execute instructions given by the instruction generator.
    All the instructions are listed in the readme,
    their usages are automatically updated at `docs/instructions.md`.
    """
    parsers: dict[str, ThrowingArgumentParser] = create_parsers()
    registered_functions: dict[str, Callable] = create_function_registry()

    def __init__(
            self,
            instruction_generator: Generator[str, None, None],
            mode: BaseInterpreter.Mode = BaseInterpreter.Mode(ProfileReader.profile().macro_interpreter_mode),
            before_next_instruction_callback: Callable[[], bool] = lambda: True
    ):
        """

        :param instruction_generator: source of the string instructions in the form of a generator
        :param mode: how to handle an invalid instruction - end the interpreting or skip it
        :param before_next_instruction_callback: callable that is asked whether the interpreter should continue working
        before executing every instruction
        """
        super().__init__()
        self.logger = getLogger(__name__)

        self._screen_match: um.screen_match.ScreenMatch | None = None
        self.instruction_generator = instruction_generator
        self.mode = mode

        self._lines: list[str] = []
        self._instruction_counter: int = -1
        self._next_instruction_idx: int = 0

        self.the_flag: bool = False
        self._end_flag: bool = False

        self.variables: dict[str, Any] = {}

        self.before_next_instruction_callback = before_next_instruction_callback

    @property
    def screen_match(self) -> um.screen_match.ScreenMatch:
        """
        Get lazily initialized ScreenMatch object used for detect, match and await
        :return: a ScreenMatch object
        """
        if self._screen_match is None:
            self._screen_match = um.screen_match.ScreenMatch()
        return self._screen_match

    def start(self) -> None:
        """
        Start the interpreter.
        :return:
        """
        while True:
            keep_going: bool = self.before_next_instruction_callback()
            self._end_flag = self._end_flag or (not keep_going)

            if self._end_flag:
                break

            self._instruction_counter = self._next_instruction_idx
            self._next_instruction_idx += 1
            try:
                while self._instruction_counter >= len(self._lines):
                    self._lines.append(next(self.instruction_generator).rstrip("\n"))
            except StopIteration:
                break

            line: str = self._lines[self._instruction_counter]

            try:
                self.logger.debug(f"interpreting: {line}")
                self._interpret(line)
            except (KeyboardController.InvalidKeyException, BaseInterpreter.InvalidInstruction):
                if self.mode == BaseInterpreter.Mode.END_ON_FAIL:
                    self.logger.exception(f"Ending interpreter session after failing to interpret: {line}")
                    return
                else:
                    self.logger.exception(f"Skipping instruction after failing to interpret: {line}")
            except KeyError as e:
                if self.mode == BaseInterpreter.Mode.END_ON_FAIL:
                    self.logger.exception(f"Ending interpreter session after: {e}")
                    return
                else:
                    self.logger.exception(f"Skipping instruction likely after trying to"
                                          f" access an uninitialized variable in the variables dict{e}")

        self.logger.debug(f"Finished interpreting")

    def _set_screen_match_section(self, parsed, full_otherwise: bool = False) -> None:
        """
        Helper method to set the compared section on screen match
        :param parsed: Namespace from parsing the instruction,
        has to have the ``section`` member of either None or string type
        :param full_otherwise: configures behaviour if parsed.section is None:
        if true, sets the compared section to the full screen,
        if false, doesn't change the compared section
        :return:
        """
        if parsed.section is not None:
            try:
                self.screen_match.set_compared_section(um.screen_match.Section.from_string(parsed.section))
            except TypeError as e:
                raise BaseInterpreter.InvalidInstruction(e)
        elif full_otherwise:
            self.screen_match.set_compared_section(um.screen_match.Section(*ProfileReader.profile().match_whole_screen))

    @staticmethod
    def _click_section(parsed, centre: tuple[int, int]) -> None:
        """
        Used InputPresser to move the mouse and click the centre position
        :param parsed: Namespace from parsing the instruction,
        with the ``click`` member of either None or pynput.mouse.Button type
        :param centre: position where to click
        :return:
        """
        if parsed.click is None or parsed.click == PyButton.unknown:
            return

        um.base_macro.InputPresser.move_mouse(centre)
        um.base_macro.InputPresser.click_mouse(parsed.click)

    def _interpret(self, line: str) -> None:
        """
        Parse and interpret a single instruction.
        :param line: the instruction to interpret
        :return:
        """
        from um.base_macro import InputPresser
        if line.startswith("---"):
            return

        items: list[str] = shlex.split(line)
        try:
            sleep(float(items[0]))
            items.pop(0)
        except ValueError:
            pass

        instruction = items[0]
        if instruction not in self.parsers.keys():
            return

        parsed = self.parsers[instruction].parse_args(items[1:])

        match instruction:
            case "press":
                InputPresser.press(parsed.key, 0)
            case "release":
                InputPresser.release(parsed.key, 0)
            case "tap":
                if parsed.with_ctrl:
                    filter_nones(InputPresser.tap_with_ctrl, parsed.key, 0, parsed.duration)
                else:
                    filter_nones(InputPresser.tap, parsed.key, 0, parsed.duration)
            case "type":
                for char in parsed.string:
                    filter_nones(InputPresser.press, Interpreter.string_to_key(char), parsed.delay)
                    filter_nones(InputPresser.release, Interpreter.string_to_key(char), parsed.duration)

            case "move":
                self.logger.debug(f"Moving mouse to: {parsed.x}, {parsed.y}")
                InputPresser.move_mouse((parsed.x, parsed.y))
            case "shift":
                self.logger.debug(f"Shifting mouse by: {parsed.x}, {parsed.y}")
                InputPresser.shift_mouse((parsed.x, parsed.y))
            case "click":
                InputPresser.click_mouse(parsed.button)
            case "scroll":
                InputPresser.scroll(parsed.x, parsed.y)

            case "jump":
                self._next_instruction_idx += parsed.by
            case "jump_if":
                if self.the_flag:
                    self._next_instruction_idx += parsed.by
            case "jump_if_not":
                if not self.the_flag:
                    self._next_instruction_idx += parsed.by
            case "set_flag":
                self.the_flag = True
            case "clear_flag":
                self.the_flag = False
            case "log":
                self.logger.log(parsed.level, f"Log instruction: {parsed.message}")
            case "end":
                self._end_flag = True

            case "detect":
                self.screen_match.load_reference_image(parsed.image_path)
                self._set_screen_match_section(parsed, True)

                result: bool | tuple[int, int] = filter_nones(
                    self.screen_match.find_match,
                    parsed.confidence_required
                )
                self.the_flag = result is not False
                if self.the_flag:
                    self._click_section(parsed, result)
            case "match":
                self.screen_match.load_reference_image(parsed.image_path)
                self._set_screen_match_section(parsed)
                self.the_flag = self.screen_match.check_match()
                if self.the_flag:
                    self._click_section(parsed, self.screen_match.capturer.section.centre)
            case "await":
                self.screen_match.load_reference_image(parsed.image_path)
                if parsed.anywhere:
                    self._set_screen_match_section(parsed, True)
                    result: bool | tuple[int, int] = filter_nones(
                        self.screen_match.wait_for_find_match,
                        parsed.timeout,
                        parsed.interval,
                        parsed.confidence_required
                    )

                    self.the_flag = result is not False
                    if self.the_flag:
                        self._click_section(parsed, result)
                else:
                    self._set_screen_match_section(parsed)
                    self.the_flag = filter_nones(
                        self.screen_match.wait_for_match,
                        parsed.timeout,
                        parsed.interval
                    )
                    if self.the_flag:
                        self._click_section(parsed, self.screen_match.capturer.section.centre)

            case "command":
                self.logger.debug(f"variables before execution: {self.variables}")
                if parsed.function_name not in self.registered_functions.keys():
                    raise BaseInterpreter.InvalidInstruction("Function name not registered")

                delay = parsed.clipboard_delay if parsed.clipboard_delay is not None \
                    else ProfileReader.profile().input_clipboard_update_delay

                if parsed.clipboard in ["copy", "full"]:
                    InputPresser.copy()
                    sleep(delay)

                func = self.registered_functions[parsed.function_name]
                arguments: list[Any] = parsed.arguments

                if parsed.clipboard != "none":
                    arguments.insert(0, pyperclip.paste())

                if parsed.pass_variables:
                    arguments.insert(0, self.variables)

                if parsed.pass_interpreter:
                    arguments.insert(0, self)

                return_value = func(*arguments)

                if parsed.clipboard != "none":
                    pyperclip.copy(
                        return_value
                    )

                if parsed.clipboard in ["paste", "full"]:
                    sleep(delay)
                    InputPresser.paste()
