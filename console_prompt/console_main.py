from prompt_toolkit import PromptSession
from logging import getLogger

from prompt_toolkit.validation import DummyValidator

from .console_base import defaults, completer
from .goto import goto_group
from .miscellaneous import _exit
from .macro import macro_group
from .tool import tool_group

def main() -> None:
    session = PromptSession()
    logger = getLogger(__name__)

    while True:
        prompt_result = session.prompt("> ", completer=completer, validator=DummyValidator())
        logger.info(f"User prompt: {prompt_result}")
        if prompt_result.strip() in defaults:
            defaults[prompt_result.strip()]()
        else:
            try:
                completer.run_action(prompt_result)
            except ValueError as e:
                logger.error(f"Invalid prompt: {prompt_result}")