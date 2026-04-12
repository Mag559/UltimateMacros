from collections.abc import Callable
from time import sleep

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
                pyperclip.copy(self.text_map(pyperclip.paste()))
                sleep(0.1)
                InputPresser.paste()



def map_text(x: str) -> str:
    try:
        number = float(x) * 0.75
        if int(number) == number:
            return str(int(number))
        return str(number)
    except ValueError:
        return x


if __name__ == "__main__":
    TextMapMacro(map_text)