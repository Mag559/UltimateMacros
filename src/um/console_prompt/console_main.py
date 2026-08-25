# noinspection PyUnusedImports
from . import action_completer_patch  # monkey patch on import

import asyncio
from collections.abc import Callable
from importlib import import_module
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
from .console_toolbar import ConsoleToolbar, TOOLBAR_STATE

from .macro import setup_macro
from .miscellaneous import setup_misc
from .tool import setup_tool


class Main:
    """
    Main class of the TUI application,
    in charge of handling the prompt toolkit session and delegating work to other classes.
    """
    def __init__(self):
        self.logger = getLogger(__name__)
        self.last_command_flag: bool = False

        # manages the canvas then drawn as the bottom toolbar
        self.toolbar: ConsoleToolbar = ConsoleToolbar(
            ProfileReader.profile().console_toolbar_width,
            ProfileReader.profile().console_toolbar_height
        )

        # manages sleeping when app is unfocused
        self.time_keeper: TimeKeeper = TimeKeeper()

        self.kb = KeyBindings()
        self._create_key_bindings()

        # sort of api given to definitions of actions to draw on the toolbar and signal losing focus
        self.console_base: ConsoleBase = ConsoleBase(self.toolbar, self.time_keeper.on_unfocused)

        self._import_actions()

        self.session = self._create_session()

        # draws something cool on the toolbar canvas
        self.console_drawer: ConsoleDrawer = ConsoleDrawer(self.toolbar, self.session.app.invalidate, self.time_keeper)

    def get_toolbar(self) -> TOOLBAR_STATE:
        """
        Wrapper for ``self.toolbar.get()``
        :return: the current, updated toolbar state from ConsoleToolbar
        """
        return self.toolbar.get()

    def _get_prompt(self) -> str | list[tuple[str, str]]:
        """
        Get the string prompting the user.
        Styled if the last command flag is raised.
        :return: plain or styled prompt
        """
        if not self.last_command_flag:
            return ProfileReader.profile().console_prompt

        return [(ProfileReader.profile().console_last_command_style, ProfileReader.profile().console_prompt)]

    def start(self) -> None:
        """
        Executes the main coroutine with asyncio.
        :return:
        """
        try:
            asyncio.run(self._main_with_patch_stdout())
        except Exception as e:
            self.logger.exception(f"Unhandled exception {e}")
            raise

    async def _main_with_patch_stdout(self) -> None:
        """
        Wraps the main ``self._run`` method in prompt toolkit context manager,
        which makes sure users output plays nice with toolbar text below.

        Attach a custom async exception handler to actually log them
        :return:
        """
        loop = asyncio.get_running_loop()
        loop.set_exception_handler(self._handle_async_exception)
        with patch_stdout():
            await self._main_loop()

    async def _main_loop(self) -> None:
        """
        Main loop of the application.
        Creates and cancels the task responsible for animation ``self.console_drawer.spin()``.
        Waits for the user prompt and passes it to ConsoleBase.
        Terminates after some time without a prompt (`console_timeout` setting in the profile).
        Handles the user's request for a prompt to be his last with SHORTCUT1 (terminates after finishing it).
        :return:
        """
        spiny_task = asyncio.create_task(self.console_drawer.spin())

        while True:
            try:
                prompt_result = await asyncio.wait_for(
                    self.session.prompt_async(self._get_prompt),
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
                self.console_base.try_to_be_of_help_to_lost_user(prompt_result)
            except TypeError as e:
                print(e.__str__())
                self.logger.error(f"Missing argument in {prompt_result} {e}")

            if self.last_command_flag:
                self.logger.info(f"Exiting due to last command flag")
                break

        spiny_task.cancel()

    def _create_key_bindings(self) -> None:
        """
        Setup key bindings for the application.
        They don't interfere when a macro is running.
        :return:
        """
        # (system focus in: \x1b [ I)
        @self.kb.add('escape', '[', 'I')
        def _(_event):
            self.time_keeper.on_focused()

        # (system focus out: \x1b [ O)
        @self.kb.add('escape', '[', 'O')
        def _(_event):
            self.time_keeper.on_unfocused()

        # Ctrl + c terminate the application
        @self.kb.add('c-c')
        def _(event):
            event.app.exit()

        # alt + ` for signalling to close the application after the end of next prompt's execution
        @self.kb.add('escape', '`')
        def _(_event):
            self.last_command_flag = not self.last_command_flag

        # ignore the ` key in isolation
        @self.kb.add("`")
        def _(_event):
            return

        @Condition
        def is_unfocused():
            return not self.time_keeper.focused

        # wake up the application from being unfocused with any key
        @self.kb.add('<any>', filter=is_unfocused)
        def _(_event):
            self.time_keeper.on_focused()

    def _import_actions(self) -> None:
        """
        Register / import actions from other scripts.
        Currently, there are 3 public scripts: miscellaneous, macro, tool
        with the possibility of adding custom ones via profiles::
            "custom_action_groups": {
                "goto": "um.console_prompt.goto"
            }
        such a script must contain a `setup_goto` method that accepts a ConsoleBase argument
        :return:
        """
        setup_macro(self.console_base)
        setup_misc(self.console_base)
        setup_tool(self.console_base)

        # name: absolute import path
        custom_action_groups: dict[str, str] = ProfileReader.profile().get_custom_attr("custom_action_groups", {})
        for custom_action_group, import_path in custom_action_groups.items():
            try:
                module = import_module(import_path, None)
            except ImportError as e:
                self.logger.exception(f"Error importing custom action group {custom_action_group}: {e}")
                continue

            setup_function_name = f"setup_{custom_action_group}"

            try:
                setup_function: Callable[[ConsoleBase], None] = getattr(module, setup_function_name)
                setup_function(self.console_base)
            except AttributeError as e:
                self.logger.exception(f"Custom action group {custom_action_group}"
                                      f" doesn't have an expected setup function {setup_function_name}: {e}")
                continue

    def _create_session(self) -> PromptSession:
        """
        Create a customized and well-connected PromptSession from prompt toolkit.
        :return: PromptSession with specified base styles, keybindings, bottom toolbar display,
        completer with access to the actions and autosuggest from history at `profile_files/history.txt`.
        """
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

    def _handle_async_exception(self, _loop: asyncio.AbstractEventLoop, context: dict) -> None:
        exception = context.get("exception")
        message = context.get("message")
        self.logger.exception(message or "Unhandled exception", exc_info=exception)


def main() -> None:
    Main().start()
