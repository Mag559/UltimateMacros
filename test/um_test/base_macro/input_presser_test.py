import unittest
from unittest.mock import patch

from pynput.keyboard import Key as PyKey
from pynput.mouse import Button as PyButton

from um.base_macro import InputPresser
from um_test.mock_pynput import MockKeyboardController, MockMouseController


class MacroEventCollectorTest(unittest.TestCase):
    def test_keyboard(self):
        event_list: list[str] = []
        mock_keyboard_controller = MockKeyboardController(event_list)
        with patch.object(InputPresser, "py_keyboard_controller", mock_keyboard_controller):
            InputPresser.paste(0)
            InputPresser.copy(0)
            InputPresser.tap_with_ctrl("n", 0)
            InputPresser.enter(0)
            InputPresser.press(PyKey.num_lock, 0)
            InputPresser.release(PyKey.num_lock, 0)
            InputPresser.tap(PyKey.cmd, 0)
            InputPresser.tab(3, 0)
            InputPresser.type("abc", 0)

        self.assertListEqual(
            event_list,
            [
                'press ctrl_l',
                'press v',
                'release v',
                'release ctrl_l',

                'press ctrl_l',
                'press c',
                'release c',
                'release ctrl_l',

                'press ctrl_l',
                'press n',
                'release n',
                'release ctrl_l',

                'press enter',
                'release enter',

                'press num_lock',
                'release num_lock',

                'press cmd',
                'release cmd',

                'press tab',
                'release tab',
                'press tab',
                'release tab',
                'press tab',
                'release tab',

                'press a',
                'release a',
                'press b',
                'release b',
                'press c',
                'release c'
            ]
        )

    def test_mouse(self):
        event_list: list[str] = []
        mock_mouse_controller = MockMouseController(event_list)
        with patch.object(InputPresser, "py_mouse_controller", mock_mouse_controller):
            InputPresser.left_click(2)
            InputPresser.click_mouse(PyButton.right)
            InputPresser.move_mouse((300, 100))
            self.assertListEqual(mock_mouse_controller.position, [300, 100])
            InputPresser.shift_mouse((-50, -100))
            self.assertListEqual(mock_mouse_controller.position, [250, 0])
            InputPresser.scroll(-10, 20)

        self.assertListEqual(
            event_list,
            [
                'click left',
                'click left',

                'click right',
                'scroll -10 20'
            ]
        )


if __name__ == '__main__':
    unittest.main()
