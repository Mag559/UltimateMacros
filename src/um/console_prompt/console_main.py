import asyncio
from logging import getLogger
from math import sin, pi
from threading import Timer
from time import time

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.styles import Style

from um.profiles import ProfileReader, PROFILES_PATH
from um.console_prompt.PenroseDrawer import PenroseDrawer
from .console_base import ConsoleBase
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

    return f"fg:#{r:02x}{g:02x}{b:02x}"


class Main:
    def __init__(self):
        self.logger = getLogger(__name__)

        self.kb = KeyBindings()
        self.create_key_bindings()
        self.focused = True

        self.toolbar: ConsoleToolbar = ConsoleToolbar(
            ProfileReader.profile().console_toolbar_width,
            ProfileReader.profile().console_toolbar_height
        )

        self.exit_timer: Timer | None = None
        self.time_backlog: float = 0.0
        self.paused_time: float = -1.0

        self.console_base: ConsoleBase = ConsoleBase(self.toolbar, self.lose_focus)

        setup_goto(self.console_base)
        setup_macro(self.console_base)
        setup_misc(self.console_base)
        setup_tool(self.console_base)

        self.session = PromptSession(
            style=Style.from_dict({
                '': ProfileReader.profile().console_prompt_style,
                "bottom-toolbar": ProfileReader.profile().console_toolbar_style,
            }),
            key_bindings=self.kb,
            bottom_toolbar=self.get_toolbar,
            validate_while_typing=False,
            completer=self.console_base.completer,
            history=FileHistory(PROFILES_PATH / "history.txt"),
            auto_suggest=AutoSuggestFromHistory()
        )


    def get_toolbar(self):
        return self.toolbar.get()


    async def run(self):
        spiny_task = asyncio.create_task(self.spin())

        while True:
            self.restart_timeout()
            prompt_result = await self.session.prompt_async(
                ProfileReader.profile().console_prompt
            )
            self.exit_timer.cancel()

            if prompt_result is None:
                self.logger.info("Prompt result is None, exiting")
                break
            self.logger.info(f"User prompt: {prompt_result}")

            try:
                self.console_base.handle_prompt(prompt_result)
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

        @self.kb.add("`")
        def _(_event):
            return


    def restart_timeout(self):
        if self.exit_timer:
            self.exit_timer.cancel()

        self.exit_timer = Timer(
            ProfileReader.profile().console_timeout,
            self.terminate
        )
        self.exit_timer.start()


    def terminate(self):
        self.session.app.exit()


    async def spin(self):
        angle: float = ProfileReader.profile().console_penrose_starting_angle
        drawer = PenroseDrawer(ProfileReader.profile().console_penrose_size)

        #TODO magic numbers
        rgb_styles: list[int] = [self.toolbar.add_new_style('') for _ in range(20)]

        for i, style in enumerate(rgb_styles):
            self.toolbar.draw_style_canvas(42, i, 82, i+1, style)


        while True:
            await asyncio.sleep(ProfileReader.profile().console_penrose_spf)
            if not self.focused:
                await self.sleep_through_pause()

            angle += ProfileReader.profile().console_penrose_spf \
                     * ProfileReader.profile().console_penrose_rotation_speed
            penrose_drawing = drawer.draw(angle)

            for i, style in enumerate(rgb_styles):
                self.toolbar.update_style(get_color_style(time() - self.time_backlog - pi * i / 10), style)
            self.toolbar.draw_on_canvas(penrose_drawing, 42, 0)

            self.session.app.invalidate()


    async def sleep_through_pause(self):
        while not self.focused:
            await asyncio.sleep(ProfileReader.profile().console_penrose_sleeping_spf)

        if self.paused_time < 0:
            return

        self.time_backlog += time() - self.paused_time


    def lose_focus(self):
        self.focused = False


def main() -> None:
    Main().start()