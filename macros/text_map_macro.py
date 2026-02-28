from collections.abc import Callable
from time import sleep

import pyperclip

from base_macro import BaseMacro, InputPresser, ImportantEvents


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


def log(func):
    def wrapper(*args, **kwargs):
        print(f"{args} in")
        result = func(*args, **kwargs)
        print(f"{result} out")
        return result
    return wrapper


# @log
def tmap(x: str) -> str:
    try:
        number = float(x) * 0.75
        if int(number) == number:
            return str(int(number))
        return str(number)
    except ValueError:
        return x


if __name__ == "__main__":
    TextMapMacro(tmap)