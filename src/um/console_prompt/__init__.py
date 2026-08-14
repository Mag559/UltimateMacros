from typing import TYPE_CHECKING
from importlib import import_module

_console_prompt_lazy_imports = {
    "main": ".console_main",
}

if TYPE_CHECKING:
    from .console_main import main

__all__ = list(_console_prompt_lazy_imports)


def __getattr__(name):
    if name not in _console_prompt_lazy_imports:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name = _console_prompt_lazy_imports[name]

    module = import_module(module_name, __name__)
    return getattr(module, name)

