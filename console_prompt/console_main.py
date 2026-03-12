from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.validation import DummyValidator
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

from logging import getLogger
import asyncio


from .console_base import defaults, completer
from .goto import goto_group
from .miscellaneous import _exit
from .macro import macro_group
from .tool import tool_group


from console_prompt.PenroseDrawer import PenroseDrawer

from time import time
from math import sin, pi

PI_066 = pi * 0.66
PI_132 = pi * 1.32

def get_color_style(current_time: float) -> str:
    r = int((sin(current_time) + 1.0) * 127.5)
    g = int((sin(current_time + PI_066) + 1.0) * 127.5)
    b = int((sin(current_time + PI_132) + 1.0) * 127.5)

    return f"bg:#{r:02x}{g:02x}{b:02x}"



def main() -> None:
    kb = KeyBindings()

    focused = [True]

    @kb.add('escape', '[', 'I')
    def _(_event):
        focused[0] = True

    # Przechwytywanie utraty focusu przez okno (Focus Out: \x1b[O)
    @kb.add('escape', '[', 'O')
    def _(_event):
        focused[0] = False

    # Wyjście z aplikacji (Ctrl+C)
    @kb.add('c-c')
    def _(event):
        event.app.exit()

    def get_toolbar():
        return [toolbar_state[0]]

    session = PromptSession(style=Style.from_dict({
        "bottom-toolbar": f"bg:#eeeeee fg:#090909",
    }))
    logger = getLogger(__name__)



    toolbar_state = [("bg:#eeeeee", "")]


    async def spin():
        angle: float = 0
        drawer = PenroseDrawer(20)
        while True:
            await asyncio.sleep(0.05)
            if not focused[0]:
                await asyncio.sleep(0.5)
                continue
            angle += 0.07
            toolbar_state[0] = (get_color_style(time()), drawer.draw(angle))

            session.app.invalidate()

    async def run():
        asyncio.create_task(spin())

        while True:
            prompt_result = await session.prompt_async(
                "> ",
                key_bindings=kb,
                completer=completer,
                validator=DummyValidator(),
                bottom_toolbar=get_toolbar,

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