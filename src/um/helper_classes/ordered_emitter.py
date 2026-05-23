from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

CALLBACK = Callable

@dataclass
class PriorityCallback:
    priority: int
    callback: CALLBACK
    def __call__(self, *args: Any, **kwargs: Any):
        self.callback(*args, **kwargs)


class OrderedEmitter:
    """
    Base emitter class that calls the registered callbacks.,
    when emit method is called
    The callback order is determined by priority:
    higher priorities are called first, lowest last
    """
    def __init__(self):
        self._callers: list[PriorityCallback] = []


    def add_caller(self, callback: CALLBACK, priority: int = 0) -> None:
        """
        Register a new callback
        :param callback: callback
        :param priority: callback priority highest first
        """
        priority_callback: PriorityCallback = PriorityCallback(priority, callback)
        for idx, elem in enumerate(self._callers):
            if elem.priority >= priority:
                continue
            self._callers.insert(idx, priority_callback)
            break
        else:
            self._callers.append(priority_callback)


    def remove_caller(self, callback: CALLBACK) -> None:
        """
        Unregister a callback
        """
        for idx, priority_callback in enumerate(self._callers):
            if priority_callback.callback == callback:
                self._callers.pop(idx)
                break
        else:
            raise ValueError("Can't remove non-registered callback")


    def _emit(self, *args: Any, **kwargs: Any) -> None:
        for caller in self._callers:
            caller(*args, **kwargs)
