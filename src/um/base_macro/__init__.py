from typing import TYPE_CHECKING
from importlib import import_module

_base_macro_lazy_imports = {
    "BaseMacro": ".base_macro",
    "MacroEventCollector": ".macro_event_collector",
    "ImportantEvent": ".macro_event_collector",
    "InputPresser": ".input_presser",
    "InputCollector": ".input_collector",
    "InputType": ".input_collector",
    "KeyInput": ".input_collector",
    "MouseInput": ".input_collector",
    "TerminationDetector": ".termination_detector",
}

if TYPE_CHECKING:
    from .base_macro import BaseMacro
    from .macro_event_collector import MacroEventCollector, ImportantEvent
    from .input_presser import InputPresser
    from .input_collector import InputCollector, InputType, KeyInput, MouseInput
    from .termination_detector import TerminationDetector

__all__ = list(_base_macro_lazy_imports)


def __getattr__(name):
    if name not in _base_macro_lazy_imports:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name = _base_macro_lazy_imports[name]

    module = import_module(module_name, __name__)
    return getattr(module, name)
