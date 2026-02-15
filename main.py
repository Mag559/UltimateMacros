import logging
from prompt_toolkit import PromptSession
from action_completer import ActionCompleter


completer = ActionCompleter()

goto_group = completer.group("goto")


@goto_group.action("wikamp")
def _goto_wikamp():
    print("Visiting wikamp!")


@goto_group.action("youtube")
def _goto_youtube():
    print("you")





if __name__ == "__main__":
    logging.basicConfig(filename='myapp.log', level=logging.DEBUG)
    session = PromptSession()

    while True:
        prompt_result = session.prompt("> ", completer=completer, validator=completer.get_validator())
        completer.run_action(prompt_result)
