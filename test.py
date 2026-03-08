from prompt_toolkit import PromptSession
from prompt_toolkit.completion import DummyCompleter

from prompt_toolkit.validation import DummyValidator


import asyncio
from prompt_toolkit.patch_stdout import patch_stdout

from render2 import draw_polygon_numpy


def main() -> None:
    session = PromptSession()

    angle = [0.001]

    def get_prompt():
        return draw_polygon_numpy(20, angle[0])

    async def spin():
        while True:
            await asyncio.sleep(0.01)
            angle[0] += 0.1
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