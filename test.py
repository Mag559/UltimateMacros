from prompt_toolkit import PromptSession
from prompt_toolkit.completion import DummyCompleter

from prompt_toolkit.validation import DummyValidator


import asyncio
from prompt_toolkit.patch_stdout import patch_stdout

from render2 import PenroseDrawer
from time import time


def main() -> None:
    session = PromptSession()
    drawer = PenroseDrawer(20)
    reference_time = [time()]
    fps = ["???"]
    frames = [0]
    angle = [0.001]

    def get_prompt():
        frames[0] += 1
        if (time() - reference_time[0]) > 1:
            fps[0] = str(frames[0])
            reference_time[0] = time()
            frames[0] = 0
        return drawer.draw(angle) + fps[0]

    async def spin():
        while True:
            await asyncio.sleep(0.06)
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