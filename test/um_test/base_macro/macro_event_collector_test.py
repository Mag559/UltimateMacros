import unittest
from time import sleep

from pynput import keyboard as py_keyboard, mouse as py_mouse

from um.profiles import ProfileReader
from um.base_macro import MacroEventCollector, ImportantEvent
from um_test.mock_pynput import MockInputCollector


def empty_callback(*_args) -> None:
    return None


class MacroEventCollectorTest(unittest.TestCase):
    def test_auto_disconnect(self):
        mock_input_collector: MockInputCollector = MockInputCollector()
        event_collector: MacroEventCollector = MacroEventCollector(mock_input_collector)
        self.assertEqual(0, len(mock_input_collector._callers))
        event_collector.run()
        self.assertEqual(1, len(mock_input_collector._callers))
        event_collector.add_callback(empty_callback)
        event_collector.remove_callback(empty_callback)
        self.assertEqual(0, len(mock_input_collector._callers))

    def test_mouse_click_events(self):
        mock_input_collector: MockInputCollector = MockInputCollector()
        event_collector: MacroEventCollector = MacroEventCollector(mock_input_collector)

        events: list[ImportantEvent] = []
        event_collector.add_callback(lambda event: events.append(event))
        event_collector.run()

        # right click
        mock_input_collector.click_anywhere(py_mouse.Button.right)
        self.assertEqual(ImportantEvent.RIGHT_CLICK, events[0])

        # middle click
        mock_input_collector.click_anywhere(py_mouse.Button.middle)
        self.assertEqual(ImportantEvent.MIDDLE_CLICK, events[1])

        # single left click should do nothing
        mock_input_collector.click_anywhere(py_mouse.Button.left)
        self.assertEqual(2, len(events))

        sleep(1.1 * ProfileReader.profile().input_double_click_time)

        # double left click
        mock_input_collector.click_anywhere(py_mouse.Button.left)
        mock_input_collector.click_anywhere(py_mouse.Button.left)
        self.assertEqual(ImportantEvent.DOUBLE_CLICK, events[2])

    def test_keyboard_events(self):
        mock_input_collector: MockInputCollector = MockInputCollector()
        event_collector: MacroEventCollector = MacroEventCollector(mock_input_collector)

        events: list[ImportantEvent] = []
        event_collector.add_callback(lambda event: events.append(event))
        event_collector.run()

        # toggle
        mock_input_collector.tap(py_keyboard.Key.num_lock)
        self.assertEqual(ImportantEvent.TOGGLE, events[0])

        # shortcut2
        mock_input_collector.press(py_keyboard.Key.alt_l)
        mock_input_collector.tap(py_keyboard.Key.cmd)
        self.assertEqual(ImportantEvent.SHORTCUT2, events[1])

        # shortcut1
        mock_input_collector.tap(py_keyboard.KeyCode.from_char('`'))
        self.assertEqual(ImportantEvent.SHORTCUT1, events[2])
        mock_input_collector.release(py_keyboard.Key.alt_l)

        mock_input_collector.press(py_keyboard.Key.ctrl_l)
        # copy
        mock_input_collector.tap(py_keyboard.KeyCode.from_char('\x03'))
        self.assertEqual(ImportantEvent.COPY, events[3])
        # pase
        mock_input_collector.tap(py_keyboard.KeyCode.from_char('\x16'))
        self.assertEqual(ImportantEvent.PASTE, events[4])
        # cut
        mock_input_collector.tap(py_keyboard.KeyCode.from_char('\x18'))
        self.assertEqual(ImportantEvent.CUT, events[5])

        mock_input_collector.release(py_keyboard.Key.ctrl_l)
        mock_input_collector.press(py_keyboard.Key.ctrl_r)

        # save
        mock_input_collector.tap(py_keyboard.KeyCode.from_char('\x13'))
        self.assertEqual(ImportantEvent.SAVE, events[6])

        mock_input_collector.release(py_keyboard.Key.ctrl_r)


if __name__ == '__main__':
    unittest.main()
