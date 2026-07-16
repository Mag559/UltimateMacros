from functools import wraps
from collections.abc import Callable
from string import ascii_lowercase, ascii_uppercase


def create_function_registry() -> dict[str, Callable]:
    registry: dict[str, Callable] = {}

    def registered(func):
        """
        Decorator to register the function in the registry
        """
        registry[func.__name__.lstrip("_")] = func

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    @registered
    def camel_to_screaming_snake_case(x: str) -> str:
        out: str = ""
        for char in x:
            if char in ascii_lowercase:
                out += char.upper()
                continue
            if char in ascii_uppercase:
                out += f'_{char}'
                continue
            out += char

        return out

    return registry
