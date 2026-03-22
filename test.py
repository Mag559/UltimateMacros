# import sys
#
# from prompt_toolkit import PromptSession
# from prompt_toolkit.completion import DummyCompleter
#
# from prompt_toolkit.validation import DummyValidator
#
#
# import asyncio
# from prompt_toolkit.patch_stdout import patch_stdout
#
# from console_prompt.PenroseDrawer import PenroseDrawer
# from prompt_toolkit.key_binding import KeyBindings
#
#
#
# def main() -> None:
#     session = PromptSession()
#     drawer = PenroseDrawer(20)
#     angle = [0.001]
#     cache = [""]
#
#     def get_prompt():
#         return cache[0]
#
#     async def spin():
#         while True:
#             await asyncio.sleep(0.03)
#             if not focused[0]:
#                 await asyncio.sleep(0.5)
#                 continue
#             angle[0] += 0.1
#             cache[0] = drawer.draw(angle)
#             session.app.invalidate()
#
#     async def run():
#         asyncio.create_task(spin())
#
#         while True:
#             prompt_result = await session.prompt_async(
#                 get_prompt,
#                 key_bindings=kb,
#                 completer=DummyCompleter(),
#                 validator=DummyValidator(),
#             )
#
#
#             print(f"do {prompt_result}")
#             break
#
#     with patch_stdout():
#         asyncio.run(run())
#
# if __name__ == "__main__":
#     sys.stdout.write('\x1b[?1004h')
#     sys.stdout.flush()
#     main()
#     sys.stdout.write('\x1b[?1004l')
#     sys.stdout.flush()