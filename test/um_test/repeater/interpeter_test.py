import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from um.base_macro import InputPresser
from um.repeater import Interpreter
from um.screen_match import ScreenMatch, Section
from um_test.mock_pynput import MockKeyboardController, MockMouseController
from um_test.screen_match import MockMss, MockCapturer


TEST_RESOURCES_DIR = Path(__file__).resolve().parents[2] / "resources"


def before_grab(calls: list[int], mock_mss: MockMss, total_calls: int, replacement_img):
    if calls[0] == total_calls - 1:
        mock_mss.img = replacement_img
    calls[0] += 1


class InterpreterTest(unittest.TestCase):
    def test_keyboard(self):
        event_list: list[str] = []
        mock_keyboard_controller = MockKeyboardController(event_list)
        interpreter: Interpreter = Interpreter(
            (ins for ins in [
                "press a",
                "release a",
                "tap b --duration 0",
                "type cde --delay 0 --duration 0",
            ])
        )
        with patch.object(InputPresser, "py_keyboard_controller", mock_keyboard_controller):
            interpreter.start()

        self.assertListEqual(
            event_list,
            [
                'press a',
                'release a',
                'press b',
                'release b',
                'press c',
                'release c',
                'press d',
                'release d',
                'press e',
                'release e'
            ]
        )

    def test_mouse(self):
        event_list: list[str] = []
        mock_mouse_controller = MockMouseController(event_list)
        interpreter: Interpreter = Interpreter(
            (ins for ins in [
                "move 100 200",
                "shift -10 20",
                "click left",
                "scroll -10 20"
            ])
        )
        with patch.object(InputPresser, "py_mouse_controller", mock_mouse_controller):
            interpreter.start()

        self.assertListEqual(mock_mouse_controller.position, [90, 220])
        self.assertListEqual(
            event_list,
            [
                "click left",
                "scroll -10 20",
            ]
        )

    def test_image_matching(self):
        event_list: list[str] = []
        interpreter: Interpreter = Interpreter(
            (ins for ins in [])
        )  # manually trigger _interpret for convenience

        calls = [0]
        fake_img = Image.open(TEST_RESOURCES_DIR / "fake_desktop.png")
        mock_mss = MockMss(before_grab=lambda: before_grab(calls, mock_mss, 4, fake_img))
        screen_match = ScreenMatch()
        screen_match.capturer = MockCapturer(Section(0, 0, 1920, 1080), mock_mss)

        interpreter._screen_match = screen_match

        mock_mouse_controller = MockMouseController(event_list)

        with open(TEST_RESOURCES_DIR / "desktop_icon.txt", "r") as f:
            correct_section = Section.from_string(f.readline().strip('\n'))

        with open(TEST_RESOURCES_DIR / "fake_icons.txt", "r") as f:
            correct_fake_section = Section.from_string(f.readline().strip('\n'))

        with patch.object(InputPresser, "py_mouse_controller", mock_mouse_controller):
            # detect
            interpreter._interpret("detect ../test/resources/desktop_icon.png --click left")
            self.assertTrue(interpreter.the_flag)
            self.assertAlmostEqual(
                mock_mouse_controller.position[0],
                correct_section.left + correct_section.width / 2,
                delta=3
            )
            self.assertAlmostEqual(
                mock_mouse_controller.position[1],
                correct_section.top + correct_section.height / 2,
                delta=3
            )
            self.assertEqual(calls[0], 1)

            # match
            interpreter._interpret("match ../test/resources/desktop_icon.png --section 0,0,300,300 --click left")
            self.assertFalse(interpreter.the_flag)
            self.assertEqual(calls[0], 2)

            # await anywhere
            interpreter._interpret(
                "await ../test/resources/fake_icons.png --anywhere --timeout 0.1 --interval 0.05 --click middle"
            )
            self.assertTrue(interpreter.the_flag)
            self.assertAlmostEqual(
                mock_mouse_controller.position[0],
                correct_fake_section.left + correct_fake_section.width / 2,
                delta=3
            )
            self.assertAlmostEqual(
                mock_mouse_controller.position[1],
                correct_fake_section.top + correct_fake_section.height / 2,
                delta=3
            )
            self.assertEqual(calls[0], 4)

            # await match
            interpreter._interpret(
                "await ../test/resources/fake_icons.png"
                " --section 0,0,300,300 --timeout 0.1 --interval 0.05 --click right"
            )
            self.assertFalse(interpreter.the_flag)
            self.assertEqual(calls[0], 7)  # one more for math failed screenshot

            self.assertListEqual(event_list, ["click left", "click middle"])

    def test_support_instructions(self):
        ins_count: int = 0
        command_count: int = 0

        def keep_going() -> bool:
            nonlocal ins_count
            ins_count += 1
            if ins_count > 10:
                return False
            return True

        def inc_test_command_count() -> None:
            nonlocal command_count
            command_count += 1

        interpreter: Interpreter = Interpreter(
            (ins for ins in ["command test_command_count++", "--- comment", "jump -3"]),
            before_next_instruction_callback=keep_going
        )
        interpreter.registered_functions["test_command_count++"] = inc_test_command_count

        interpreter.start()

        self.assertEqual(command_count, 4)
        self.assertEqual(ins_count, 11)

        ins_count = 0
        command_count = 0

        interpreter = Interpreter(
            (ins for ins in ["clear_flag", "jump_if 3", "set_flag", "jump_if 1", "jump -1", "end", "---", "---"]),
            before_next_instruction_callback=keep_going
        )
        interpreter.start()

        self.assertEqual(ins_count, 6)  # keep_going checks before checking end flag and whether out of instructions


if __name__ == '__main__':
    unittest.main()
