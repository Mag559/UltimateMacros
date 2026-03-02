import asyncio
from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout, Window
from prompt_toolkit.layout.controls import FormattedTextControl

frames = ["|", "/", "-", "\\"]
index = 0

def get_text():
    return f"Loading... {frames[index]}"

control = FormattedTextControl(get_text)
window = Window(content=control)

app = Application(layout=Layout(window), full_screen=False)

async def animate():
    global index
    while True:
        await asyncio.sleep(0.1)
        index = (index + 1) % len(frames)
        app.invalidate()

async def main():
    asyncio.create_task(animate())
    await app.run_async()

asyncio.run(main())