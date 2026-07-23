from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .profiles import ProfileReader
    from .console_prompt import main

__all__ = ["ProfileReader", "main"]


def __getattr__(name):
    if name == "ProfileReader":
        from .profiles import ProfileReader
        return ProfileReader
    if name == "main":
        from .console_prompt import main
        return main
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

