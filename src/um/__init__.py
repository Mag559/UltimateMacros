from typing import TYPE_CHECKING
from importlib import import_module

_tools_lazy_imports = {
    "main": ".console_prompt",
    "PROJECT_ROOT": ".profiles",
    "ProfileReader": ".profiles",
}

if TYPE_CHECKING:
    from .profiles import ProfileReader, PROJECT_ROOT
    from .console_prompt import main

__all__ = list(_tools_lazy_imports)


def __getattr__(name):
    if name not in _tools_lazy_imports:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name = _tools_lazy_imports[name]

    module = import_module(module_name, __name__)
    return getattr(module, name)
