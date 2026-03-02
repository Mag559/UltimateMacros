from prompt_toolkit import PromptSession
from logging import getLogger

from prompt_toolkit.validation import DummyValidator

from .console_base import defaults, completer
from .goto import goto_group
from .miscellaneous import _exit
from .macro import macro_group
from .tool import tool_group

import asyncio
from itertools import cycle
from prompt_toolkit.patch_stdout import patch_stdout

frames = cycle(["|", "/", "-", "\\"])

def main() -> None:
    session = PromptSession()
    logger = getLogger(__name__)

    spinner = {"frame": next(frames)}

    def get_prompt():
        return f"{spinner['frame']} "

    async def spin():
        while True:
            await asyncio.sleep(0.1)
            spinner["frame"] = next(frames)
            session.app.invalidate()

    async def run():
        asyncio.create_task(spin())

        while True:
            prompt_result = await session.prompt_async(
                get_prompt,
                completer=completer,
                validator=DummyValidator(),
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