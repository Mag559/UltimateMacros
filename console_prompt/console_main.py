from threading import Timer

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


class Main:
    def __init__(self):
        self.logger = getLogger(__name__)

        self.kb = KeyBindings()
        self.focused = True

        self.session = PromptSession(style=Style.from_dict({
            "bottom-toolbar": f"bg:#eeeeee fg:#090909",
        }))

        self.toolbar_state = ("bg:#eeeeee", "")


        self.exit_timer: Timer | None = None

        self.restart_timeout()


    def get_toolbar(self):
        return [self.toolbar_state]


    async def run(self):
        spiny_task = asyncio.create_task(self.spin())

        while True:
            prompt_result = await self.session.prompt_async(
                "> ",
                key_bindings=self.kb,
                completer=completer,
                validator=DummyValidator(),
                bottom_toolbar=self.get_toolbar,

            )
            if prompt_result is None:
                self.logger.info("Prompt result is None, exiting")
                break
            self.logger.info(f"User prompt: {prompt_result}")
            self.restart_timeout()

            if prompt_result.strip() in defaults:
                defaults[prompt_result.strip()]()
            else:
                try:
                    completer.run_action(prompt_result)
                except ValueError:
                    self.logger.error(f"Invalid prompt: {prompt_result}")

        spiny_task.cancel()


    def start(self):
        with patch_stdout():
            asyncio.run(self.run())


    def create_key_bindings(self):
        @self.kb.add('escape', '[', 'I')
        def _(_event):
            self.focused = True

        # Przechwytywanie utraty focusu przez okno (Focus Out: \x1b[O)
        @self.kb.add('escape', '[', 'O')
        def _(_event):
            self.focused = False

        # Wyjście z aplikacji (Ctrl+C)
        @self.kb.add('c-c')
        def _(event):
            event.app.exit()


    def restart_timeout(self):
        if self.exit_timer:
            self.exit_timer.cancel()
        self.exit_timer = Timer(100, self.terminate)
        self.exit_timer.start()


    def terminate(self):
        self.session.app.exit()

    async def spin(self):
        angle: float = 0
        drawer = PenroseDrawer(20)
        while True:
            await asyncio.sleep(0.05)
            if not self.focused:
                await asyncio.sleep(0.5)
                continue
            angle += 0.07
            self.toolbar_state = (get_color_style(time()), drawer.draw(angle))

            self.session.app.invalidate()


def main() -> None:
    Main().start()