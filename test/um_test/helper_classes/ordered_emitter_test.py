import unittest

from um.helper_classes import OrderedEmitter


class OrderedEmitterTest(unittest.TestCase):
    def test_emission_order(self):
        emitter = OrderedEmitter()
        calls = []
        first_callable = lambda: calls.append("1_0")
        emitter.add_caller(first_callable, 1)
        emitter.add_caller(lambda: calls.append("10"), 10)
        emitter.add_caller(lambda: calls.append("1_1"), 1)

        emitter._emit()
        self.assertListEqual(calls, ["10", "1_0", "1_1"])
        emitter.remove_caller(first_callable)
        self.assertRaises(ValueError, emitter.remove_caller, first_callable)
        calls = []

        emitter._emit()
        self.assertListEqual(calls, ["10", "1_1"])

    def test_modification_mid_emission(self):
        emitter = OrderedEmitter()
        calls = []
        first = lambda: calls.append("1")
        second = lambda: emitter.remove_caller(first)
        third = lambda: calls.append("3")
        fourth = lambda: emitter.add_caller(fifth, 1)
        fifth = lambda: calls.append("5")

        emitter.add_caller(first, 5)
        emitter.add_caller(second, 4)
        emitter.add_caller(third, 3)
        emitter.add_caller(fourth, 2)

        emitter._emit()
        self.assertListEqual(calls, ["1", "3"])

        emitter.remove_caller(second)

        calls = []
        emitter._emit()
        self.assertListEqual(calls, ["3", "5"])


if __name__ == '__main__':
    unittest.main()
