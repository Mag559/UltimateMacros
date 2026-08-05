from typing import TYPE_CHECKING
from importlib import import_module

_repeater_lazy_imports = {
    "BaseInterpreter": ".base_interpreter",
    "Interpreter": ".interpreter",
    "build_file_interpreter": ".interpreter",
    "Recorder": ".recorder",
    "RecorderMacro": ".recorder_macro",
    "InterpreterMacro": ".interpreter_macro",
    "RepeaterMacro": ".repeater_macro",
    "MACRO_FILES": ".repeater_macro",
}

if TYPE_CHECKING:
    from .base_interpreter import BaseInterpreter
    from .interpreter import Interpreter, build_file_interpreter
    from .recorder import Recorder
    from .recorder_macro import RecorderMacro
    from .interpreter_macro import InterpreterMacro
    from .repeater_macro import RepeaterMacro, MACRO_FILES

__all__ = _repeater_lazy_imports.keys()


def __getattr__(name):
    if name not in _repeater_lazy_imports.keys():
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name = _repeater_lazy_imports[name]

    module = import_module(module_name, __name__)
    return getattr(module, name)
