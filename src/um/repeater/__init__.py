from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base_interpreter import BaseInterpreter
    from .interpreter import Interpreter, build_file_interpreter
    from .recorder import Recorder
    from .recorder_macro import RecorderMacro
    from .interpreter_macro import InterpreterMacro
    from .repeater_macro import RepeaterMacro, MACRO_FILES

__all__ = [
    "BaseInterpreter", "Interpreter", "build_file_interpreter",
    "Recorder", "RecorderMacro",
    "InterpreterMacro",
    "RepeaterMacro", "MACRO_FILES"
]


def __getattr__(name):
    if name == "BaseInterpreter":
        from .base_interpreter import BaseInterpreter
        return BaseInterpreter
    if name == "Interpreter":
        from .interpreter import Interpreter
        return Interpreter
    if name == "build_file_interpreter":
        from .interpreter import build_file_interpreter
        return build_file_interpreter
    if name == "Recorder":
        from .recorder import Recorder
        return Recorder
    if name == "RecorderMacro":
        from .recorder_macro import RecorderMacro
        return RecorderMacro
    if name == "InterpreterMacro":
        from .interpreter_macro import InterpreterMacro
        return InterpreterMacro
    if name == "RepeaterMacro":
        from .repeater_macro import RepeaterMacro
        return RepeaterMacro
    if name == "MACRO_FILES":
        from .repeater_macro import MACRO_FILES
        return MACRO_FILES
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
