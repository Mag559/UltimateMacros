from action_completer import ActionCompleter

class ConsoleBase:
    def __init__(self):
        self.completer = ActionCompleter()
        self.defaults = {}

    def default(self, func):
        """
        Decorator to register an action in place of an action group
        e.i. bind `goto` command to an action, when there is a 'goto' action group defined
        """
        self.defaults[func.__name__.lstrip("_").replace("_", " ")] = func
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper


    def handle_prompt(self, prompt_result: str):
        stripped_prompt = prompt_result.strip()
        if stripped_prompt in self.defaults:
            self.defaults[stripped_prompt]()
        else:
            self.completer.run_action(prompt_result)