from enum import Enum
from typing import Callable, List, Protocol, TypeVar


class Emitter:
    def __init__(self):
        self.callers: List[Callable] = []

    def add_caller(self, call: Callable):
        self.callers.append(call)

    def remove_caller(self, call: Callable):
        self.callers.remove(call)

    def emit(self, event_code: Enum):
        for caller in self.callers:
            caller(event_code)


E = TypeVar("E", bound=Enum)

class Observer(Protocol[E]):
    def update(self, event_code: E):
        pass


    def subscribe(self, emitter: Emitter):
        emitter.add_caller(self.update)


    def unsubscribe(self, emitter: Emitter):
        emitter.remove_caller(self.update)
