import ast
from functools import wraps
from collections.abc import Callable
from string import ascii_lowercase, ascii_uppercase
from random import random
from typing import Any


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
    def set_variable(variables: dict[str, Any], variable_name: str, type_name: str, initial_value_str: str) -> None:
        typed_initial_value: Any
        if type_name == "str":
            typed_initial_value = initial_value_str
        else:
            typed_initial_value = ast.literal_eval(initial_value_str)
        variables[variable_name] = typed_initial_value

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

    coin_streak: int = 0

    @registered
    def coin_toss(interpreter) -> None:
        nonlocal coin_streak
        heads: bool = random() > 0.5
        if heads:
            coin_streak += 1
        else:
            coin_streak = 0
        interpreter.the_flag = heads

    @registered
    def is_coin_toss_won(interpreter) -> None:
        nonlocal coin_streak
        interpreter.the_flag = coin_streak >= 3

    return registry
