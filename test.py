from prompt_toolkit import PromptSession
from prompt_toolkit.completion import DummyCompleter

from prompt_toolkit.validation import DummyValidator


import asyncio
from itertools import cycle
from prompt_toolkit.patch_stdout import patch_stdout

frames = cycle(["|", "/", "-", "\\"])

def main() -> None:
    session = PromptSession()

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
                completer=DummyCompleter(),
                validator=DummyValidator(),
            )


            print(f"do {prompt_result}")
            break

    with patch_stdout():
        asyncio.run(run())

if __name__ == "__main__":
    main()