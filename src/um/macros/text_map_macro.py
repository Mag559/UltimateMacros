import re
from logging import getLogger, Logger
from collections.abc import Callable
from string import ascii_lowercase, ascii_uppercase
from time import sleep

import pyperclip

from um.profiles import ProfileReader
from um.base_macro import BaseMacro, InputPresser, ImportantEvents


class TextMapMacro(BaseMacro):
    """
    Ctrl+c the text,
    the copied text is processed by the `text_map` function
    and pasted in place of the original text.
    """
    def __init__(self, text_map: Callable[[str], str]):
        self.text_map_logger: Logger = getLogger(__name__)
        super().__init__()
        self.text_map = text_map


    def _update(self, event_code: ImportantEvents):
        super()._update(event_code)

        match event_code:
            case ImportantEvents.COPY:
                sleep(ProfileReader.profile().macro_text_map_copy_delay)
                inp: str = pyperclip.paste()
                self.text_map_logger.debug(f"Text map macro input: {inp}")

                out: str = self.text_map(pyperclip.paste())
                self.text_map_logger.debug(f"Text map macro output: {out}")

                pyperclip.copy(out)
                InputPresser.paste(ProfileReader.profile().macro_text_map_paste_delay)



def camel_case_to_screaming_snake_case(x: str) -> str:
    out: str = ""
    for char in x:
        if char in ascii_lowercase:
            out += char.upper()
            continue
        if char in ascii_uppercase:
            out += f'_{char}'
            continue
        out += char

    return out


def surround_with(x: str, left: str, right: str) -> str:
    x = re.sub(r'(?<!\\)_', r'\\_', x)
    return left + x + right

