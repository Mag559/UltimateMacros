from typing import TYPE_CHECKING
from importlib import import_module

_helper_classes_lazy_imports = {
    "CALLBACK": ".ordered_emitter",
    "OrderedEmitter": ".ordered_emitter",
    "SingletonMeta": ".meta_singleton",
    "LoggingThread": ".logging_thread",
}

if TYPE_CHECKING:
    from .meta_singleton import SingletonMeta
    from .ordered_emitter import OrderedEmitter, CALLBACK
    from .logging_thread import LoggingThread

__all__ = list(_helper_classes_lazy_imports)


def __getattr__(name):
    if name not in _helper_classes_lazy_imports:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name = _helper_classes_lazy_imports[name]

    module = import_module(module_name, __name__)
    return getattr(module, name)
