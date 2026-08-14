from typing import TYPE_CHECKING
from importlib import import_module


_screen_match_lazy_imports = {
    "Section": ".capturer",
    "Capturer": ".capturer",
    "Matcher": ".matcher",
    "ScreenMatch": ".screen_match",
    "REFERENCE_IMAGES": ".screen_match",
}

if TYPE_CHECKING:
    from .capturer import Section, Capturer
    from .matcher import Matcher
    from .screen_match import ScreenMatch, REFERENCE_IMAGES

__all__ = list(_screen_match_lazy_imports)


def __getattr__(name):
    if name not in _screen_match_lazy_imports:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name = _screen_match_lazy_imports[name]

    module = import_module(module_name, __name__)
    return getattr(module, name)
