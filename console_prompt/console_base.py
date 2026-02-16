from action_completer import ActionCompleter

completer = ActionCompleter()
defaults = {}

def default(func):
    defaults[func.__name__.lstrip("_").replace("_", " ")] = func
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper