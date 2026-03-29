from threading import Timer
import asyncio
from logging import getLogger
from math import sin, pi
from time import time

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.validation import DummyValidator
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style


from .console_base import defaults, completer
from src.console_prompt.PenroseDrawer import PenroseDrawer
from .console_toolbar import ConsoleToolbar

from .goto import setup_goto
from .macro import setup_macro
from .miscellaneous import setup_misc
from .tool import setup_tool


PI_066 = pi * 0.66
PI_132 = pi * 1.32

def get_color_style(current_time: float) -> str:
    r = int((sin(current_time) + 1.0) * 127.5)
    g = int((sin(current_time + PI_066) + 1.0) * 127.5)
    b = int((sin(current_time + PI_132) + 1.0) * 127.5)

    return f"bg:#{r:02x}{g:02x}{b:02x}"


def get_color_style_weighted(brightness: float) -> str:
    r = min(255, int(255 * brightness))
    g = min(255, int(255 * brightness))
    b = min(255, int(255 * brightness))

    return f"bg:#{r:02x}{g:02x}{b:02x}"


class Main:
    def __init__(self):
        self.logger = getLogger(__name__)

        self.kb = KeyBindings()
        self.create_key_bindings()
        self.focused = True

        self.session = PromptSession(
            style=Style.from_dict({
                "bottom-toolbar": f"bg:#eeeeee fg:#090909",
            }),
            key_bindings=self.kb,
            bottom_toolbar=self.get_toolbar
        )

        self.toolbar: ConsoleToolbar = ConsoleToolbar(20, 20)


        self.exit_timer: Timer | None = None
        self.time_backlog: float = 0.0
        self.paused_time: float = -1.0

        setup_goto()
        setup_macro()
        setup_misc()
        setup_tool()


    def get_toolbar(self):
        return self.toolbar.get()


    async def run(self):
        spiny_task = asyncio.create_task(self.spin())

        while True:
            self.restart_timeout()
            prompt_result = await self.session.prompt_async(
                "> ",
                completer=completer,
                validator=DummyValidator()
            )
            self.exit_timer.cancel()

            if prompt_result is None:
                self.logger.info("Prompt result is None, exiting")
                break
            self.logger.info(f"User prompt: {prompt_result}")

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
        # Przechwytywanie uzyskania focusu przez okno (Focus In: \x1b[I)
        @self.kb.add('escape', '[', 'I')
        def _(_event):
            self.focused = True
            # accounting for the paused time is further deferred to when the spin task exits slow sleep loop

        # Przechwytywanie utraty focusu przez okno (Focus Out: \x1b[O)
        @self.kb.add('escape', '[', 'O')
        def _(_event):
            self.focused = False
            self.paused_time = time()

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
        drawer = PenroseDrawer(10)
        big_drawer = PenroseDrawer(20)
        while True:
            await asyncio.sleep(0.05)
            if not self.focused:
                await self.sleep_through_pause()
            angle += 0.07
            penrose_drawing = drawer.draw(angle) + "\n"
            big_drawing = big_drawer.draw(angle)
            for x in range(20):
                for y in range(20):
                    brightness: float = 0
                    match big_drawing[2 * x + y * 41]:
                        case '#':
                            brightness = 1.5
                        case '*':
                            brightness = 0.6
                        case '.':
                            brightness = 0.2
                        case _:
                            brightness = 0.01
                    self.toolbar.update(
                        x, y,
                        penrose_drawing,
                        get_color_style_weighted(brightness)
                    )


            self.session.app.invalidate()


    async def sleep_through_pause(self):
        while not self.focused:
            await asyncio.sleep(0.5)

        if self.paused_time < 0:
            return

        self.time_backlog += time() - self.paused_time


def main() -> None:
    Main().start()