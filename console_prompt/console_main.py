from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.validation import DummyValidator
from prompt_toolkit.key_binding import KeyBindings

from logging import getLogger
import asyncio


from .console_base import defaults, completer
from .goto import goto_group
from .miscellaneous import _exit
from .macro import macro_group
from .tool import tool_group


from console_prompt.PenroseDrawer import PenroseDrawer
from prompt_toolkit.styles import Style, DynamicStyle
from time import time
from math import sin


def get_hex_colour_part(val) -> str:
    t = hex(int(sin(val) * 128 + 128))[2:]
    if len(t) == 1:
        t = '0' + t
    return t


def get_style():
    current_time = time()
    return Style.from_dict({
        "bottom-toolbar":
            f"bg:#{get_hex_colour_part(current_time)}{get_hex_colour_part(current_time + 72)}{get_hex_colour_part(current_time + 144)}"
            f" fg:#090909",
    })


def main() -> None:
    kb = KeyBindings()

    focused = [True]

    @kb.add('escape', '[', 'I')
    def _(event):
        focused[0] = True

    # Przechwytywanie utraty focusu przez okno (Focus Out: \x1b[O)
    @kb.add('escape', '[', 'O')
    def _(event):
        focused[0] = False

    # Wyjście z aplikacji (Ctrl+C)
    @kb.add('c-c')
    def _(event):
        event.app.exit()

    session = PromptSession(style=DynamicStyle(get_style))
    logger = getLogger(__name__)

    drawer = PenroseDrawer(20)
    angle = [0.]
    cache = [""]

    def get_prompt():
        return cache[0]

    async def spin():
        while True:
            await asyncio.sleep(0.03)
            if not focused[0]:
                await asyncio.sleep(0.5)
                continue
            angle[0] += 0.07
            cache[0] = drawer.draw(angle)
            session.app.invalidate()

    async def run():
        asyncio.create_task(spin())

        while True:
            prompt_result = await session.prompt_async(
                "> ",
                key_bindings=kb,
                completer=completer,
                validator=DummyValidator(),
                bottom_toolbar=get_prompt,

            )

            logger.info(f"User prompt: {prompt_result}")

            if prompt_result.strip() in defaults:
                defaults[prompt_result.strip()]()
            else:
                try:
                    completer.run_action(prompt_result)
                except ValueError:
                    logger.error(f"Invalid prompt: {prompt_result}")

    with patch_stdout():
        asyncio.run(run())