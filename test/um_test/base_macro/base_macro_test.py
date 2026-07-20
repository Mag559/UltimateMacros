import unittest
from threading import Thread
from time import sleep

from pynput import keyboard as py_keyboard

from um.base_macro import BaseMacro, MacroEventCollector, TerminationDetector
from um_test.mock_pynput import MockInputCollector


def trigger_shortcut(mock_input_collector):
    mock_input_collector.press(py_keyboard.Key.alt_l)
    mock_input_collector.tap(py_keyboard.KeyCode.from_char('`'))
    mock_input_collector.release(py_keyboard.Key.alt_l)


class BaseMacroTest(unittest.TestCase):
    def test_asynchronous_start(self):
        base_macro = BaseMacro(MockInputCollector(), 10)
        t = Thread(target=base_macro._run)

        self.assertFalse(base_macro._exit_timer.is_alive())
        t.start()
        sleep(0.1)
        self.assertFalse(t.is_alive())
        self.assertTrue(base_macro._exit_timer.is_alive())

        base_macro.stop()

    def test_start(self):
        base_macro = BaseMacro(MockInputCollector(), 10)
        t = Thread(target=base_macro.start)

        self.assertFalse(base_macro._exit_timer.is_alive())
        t.start()
        sleep(0.1)
        self.assertTrue(t.is_alive())
        self.assertTrue(base_macro._exit_timer.is_alive())

        base_macro.stop()
        sleep(0.1)
        self.assertFalse(t.is_alive())
        self.assertFalse(base_macro._exit_timer.is_alive())

    def test_timeout(self):
        base_macro = BaseMacro(MockInputCollector(), 0.1)
        t = Thread(target=base_macro.start)
        t.start()
        sleep(0.15)
        self.assertFalse(t.is_alive())
        self.assertFalse(base_macro._exit_timer.is_alive())

    def test_shortcut_termination(self):
        mock_input_collector = MockInputCollector()
        terminator = TerminationDetector(3, 0.2)
        base_macro = BaseMacro(MacroEventCollector(mock_input_collector), 10)
        base_macro._terminator = terminator

        t = Thread(target=base_macro.start)
        t.start()
        sleep(0.01)

        trigger_shortcut(mock_input_collector)

        sleep(0.25)
        self.assertTrue(t.is_alive())

        trigger_shortcut(mock_input_collector)
        trigger_shortcut(mock_input_collector)
        trigger_shortcut(mock_input_collector)

        sleep(0.05)

        self.assertFalse(base_macro._exit_timer.is_alive())
        self.assertFalse(t.is_alive())


if __name__ == '__main__':
    unittest.main()
