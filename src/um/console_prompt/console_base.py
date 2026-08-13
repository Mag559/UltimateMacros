from collections.abc import Callable
from functools import wraps

from action_completer import ActionCompleter

from .console_toolbar import ConsoleToolbar


class ConsoleBase:
    """
    A bridge between Main (console_main) and actions defined in other scripts.
    Exposes an api of a few operations like access to the toolbar class and releasing focus
    to functions serving as prompt_toolkit actions.
    """
    def __init__(self, console_toolbar: ConsoleToolbar, focus_release: Callable[[], None]):
        """

        :param console_toolbar: a console toolbar instance
        :param focus_release: callable for signaling a section of Main running
        despite the main thread processing an action that it should rest
        (most notably stop the triangle spinning animation)
        """
        self.completer = ActionCompleter()
        self.defaults = {}
        self.toolbar = console_toolbar
        self.focus_release = focus_release

    def default(self, func):
        """
        Decorator to register an action in place of an action group
        e.i. bind `goto` command to an action, when there is a 'goto' action group defined
        :param func: function to be decorated
        """
        self.defaults[func.__name__.lstrip("_").replace("_", " ")] = func

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    def handle_prompt(self, prompt_result: str) -> None:
        """
        Find the function appropriate for the given user prompt and call it.
        Prioritize defaults, otherwise hand it over to a prompt_toolkit action completer.
        :param prompt_result: user's prompt
        :return:
        """
        stripped_prompt = prompt_result.strip()
        if stripped_prompt in self.defaults:
            self.defaults[stripped_prompt]()
        else:
            self.completer.run_action(prompt_result)
