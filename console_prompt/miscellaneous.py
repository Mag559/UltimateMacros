from .console_base import completer

@completer.action("exit")
@completer.action("quit")
@completer.action("q")
def _exit():
    quit(0)