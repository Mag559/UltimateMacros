from um.repeater import Recorder


class MockKeyboardController:
    def __init__(self, event_list: list[str]):
        self.event_list = event_list

    def press(self, key):
        self.event_list.append(f"press {Recorder.key_to_string(key)}")

    def release(self, key):
        self.event_list.append(f"release {Recorder.key_to_string(key)}")

    def tap(self, key):
        self.press(key)
        self.release(key)


class MockMouseController:
    def __init__(self, event_list: list[str]):
        self.event_list = event_list
        self.position: list[int] = [0, 0]

    def click(self, button, count: int = 1):
        for _ in range(count):
            self.event_list.append(f"click {button.name}")

    def move(self, x, y):
        self.position[0] += x
        self.position[1] += y

    def scroll(self, x, y):
        self.event_list.append(f"scroll {x} {y}")
