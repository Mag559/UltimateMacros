from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

CALLBACK = Callable


@dataclass(frozen=True)
class PriorityCallback:
    """
    Dataclass for a Callable with an associated int priority
    """
    priority: int
    callback: CALLBACK

    def __call__(self, *args: Any, **kwargs: Any):
        self.callback(*args, **kwargs)


class OrderedEmitter:
    """
    Calls the registered callbacks, when the emit method is called on itself.

    The callback order is determined by priority:
    higher priorities are called first, lowest last
    """

    def __init__(self):
        self._callers: list[PriorityCallback] = []

    def run(self) -> None:
        """
        Empty method to be overridden by derived classes.
        To consciously start emitting, often asynchronous, events.
        :return:
        """
        pass

    def add_callback(self, callback: CALLBACK, priority: int = 0) -> None:
        """
        Register a new callback and insert it into right place according to priority
        :param callback: Callable to be registered, derived classes should specify the desired signature
        :param priority: callback priority, highest first
        :return:
        """
        priority_callback: PriorityCallback = PriorityCallback(priority, callback)
        for idx, elem in enumerate(self._callers):
            if elem.priority >= priority:
                continue
            self._callers.insert(idx, priority_callback)
            break
        else:
            self._callers.append(priority_callback)

    def remove_callback(self, callback: CALLBACK) -> None:
        """
        Unregister a callback
        :param callback:
        :return:
        :raises ValueError: if the callback is not registered
        """
        for idx, priority_callback in enumerate(self._callers):
            if priority_callback.callback == callback:
                self._callers.pop(idx)
                break
        else:
            raise ValueError("Can't remove non-registered callback")

    def _emit(self, *args: Any, **kwargs: Any) -> None:
        """
        Call the already sorted callbacks
        :param args:
        :param kwargs:
        :return:
        """
        for caller in self._callers.copy():
            caller(*args, **kwargs)
