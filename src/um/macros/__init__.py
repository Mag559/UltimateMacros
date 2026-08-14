from typing import TYPE_CHECKING
from importlib import import_module

_macros_lazy_imports = {
    "TextMapMacro": ".text_map_macro",
    "surround_with": ".text_map_macro",
    "ClipboardMacro": ".clipboard_macro",
}

if TYPE_CHECKING:
    from .text_map_macro import TextMapMacro, surround_with
    from .clipboard_macro import ClipboardMacro

__all__ = list(_macros_lazy_imports)


def __getattr__(name):
    if name not in _macros_lazy_imports:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name = _macros_lazy_imports[name]

    module = import_module(module_name, __name__)
    return getattr(module, name)
