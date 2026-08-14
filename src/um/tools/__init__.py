from typing import TYPE_CHECKING
from importlib import import_module

_tools_lazy_imports = {
    "ScreenshotPreview": ".screenshot_preview",
}

if TYPE_CHECKING:
    from .screenshot_preview import ScreenshotPreview

__all__ = list(_tools_lazy_imports)


def __getattr__(name):
    if name not in _tools_lazy_imports:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name = _tools_lazy_imports[name]

    module = import_module(module_name, __name__)
    return getattr(module, name)
