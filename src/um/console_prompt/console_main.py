import asyncio
from logging import getLogger

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.filters import Condition
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.styles import Style

from um.profiles import ProfileReader, PROFILES_PATH
from .console_base import ConsoleBase
from .console_drawer import ConsoleDrawer
from .console_time_keeper import TimeKeeper
from .console_toolbar import ConsoleToolbar
from .goto import setup_goto
from .macro import setup_macro
from .miscellaneous import setup_misc
from .tool import setup_tool


class Main:
    def __init__(self):
        self.logger = getLogger(__name__)
        self.last_command_flag: bool = False

        # manages the canvas then drawn as the bottom toolbar
        self.toolbar: ConsoleToolbar = ConsoleToolbar(
            ProfileReader.profile().console_toolbar_width,
            ProfileReader.profile().console_toolbar_height
        )

        # manages sleeping when app is unfocused
        self.time_keeper: TimeKeeper = TimeKeeper(self.terminate)

        self.kb = KeyBindings()
        self.create_key_bindings()

        # sort of api given to definitions of actions to draw on the toolbar and signal losing focus
        self.console_base: ConsoleBase = ConsoleBase(self.toolbar, self.time_keeper.on_unfocused)

        self.import_actions()

        self.session = self.create_session()

        # draws something cool on the toolbar canvas
        self.console_drawer: ConsoleDrawer = ConsoleDrawer(self.toolbar, self.session.app.invalidate, self.time_keeper)

    def get_toolbar(self):
        return self.toolbar.get()

    def get_prompt(self):
        if not self.last_command_flag:
            return ProfileReader.profile().console_prompt

        return [(ProfileReader.profile().console_last_command_style, ProfileReader.profile().console_prompt)]

    def start(self):
        with patch_stdout():
            asyncio.run(self.run())

    async def run(self):
        spiny_task = asyncio.create_task(self.console_drawer.spin())

        while True:
            try:
                prompt_result = await asyncio.wait_for(
                    self.session.prompt_async(self.get_prompt),
                    timeout=ProfileReader.profile().console_timeout
                )
            except asyncio.TimeoutError:
                self.logger.info("Prompt timed out, exiting")
                break

            self.logger.info(f"User prompt: {prompt_result}")

            try:
                self.console_base.handle_prompt(prompt_result)
            except ValueError:
                self.logger.error(f"Invalid prompt: {prompt_result}")
            except TypeError as e:
                print(e.__str__())
                self.logger.error(f"Missing argument in {prompt_result} {e}")

            if self.last_command_flag:
                self.logger.info(f"Exiting due to last command flag")
                break

        spiny_task.cancel()

    def create_key_bindings(self):
        # Przechwytywanie uzyskania focusu przez okno (Focus In: \x1b[I)
        @self.kb.add('escape', '[', 'I')
        def _(_event):
            self.time_keeper.on_focused()

        # Przechwytywanie utraty focusu przez okno (Focus Out: \x1b[O)
        @self.kb.add('escape', '[', 'O')
        def _(_event):
            self.time_keeper.on_unfocused()

        # Wyjście z aplikacji (Ctrl+C)
        @self.kb.add('c-c')
        def _(event):
            event.app.exit()

        @self.kb.add('escape', '`')
        def _(_event):
            self.last_command_flag = not self.last_command_flag

        @self.kb.add("`")
        def _(_event):
            return

        @Condition
        def is_unfocused():
            return not self.time_keeper.focused

        @self.kb.add('<any>', filter=is_unfocused)
        def _(_event):
            self.time_keeper.on_focused()

    def import_actions(self):
        setup_goto(self.console_base)
        setup_macro(self.console_base)
        setup_misc(self.console_base)
        setup_tool(self.console_base)

    def create_session(self) -> PromptSession:
        return PromptSession(
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

    def terminate(self):
        self.session.app.exit()


def main() -> None:
    Main().start()
