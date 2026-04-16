from collections.abc import Callable
from time import sleep
from string import ascii_lowercase, ascii_uppercase

import pyperclip

from um.base_macro import BaseMacro, InputPresser, ImportantEvents


class TextMapMacro(BaseMacro):
    """
    Ctrl+c the text,
    the copied text is processed by the `text_map` function
    and pasted in place of the original text.
    """
    def __init__(self, text_map: Callable[[str], str]):
        super().__init__()
        self.text_map = text_map

    def update(self, event_code: ImportantEvents):
        super().update(event_code)

        match event_code:
            case ImportantEvents.COPY:
                x = self.text_map(pyperclip.paste())
                print(x)
                pyperclip.copy(x)
                sleep(0.3)
                InputPresser.paste()



def map_text(x: str) -> str:
    # variable_type, _, rest = x.partition(' ')
    # variable_name, _, rest = rest.partition(' ')
    #
    # out: str = ""
    # for char in variable_name:
    #     if char in ascii_lowercase:
    #         out += char.upper()
    #         continue
    #     if char in ascii_uppercase:
    #         out += f'_{char}'
    #         continue
    #     out += char
    #
    # return f"{variable_type} {out} {rest}"

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


if __name__ == "__main__":
    TextMapMacro(map_text).start()