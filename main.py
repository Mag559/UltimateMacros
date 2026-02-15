import logging
from prompt_toolkit import PromptSession
from action_completer import ActionCompleter

from firefox_handling.wikamp import FirefoxHandler

completer = ActionCompleter()

goto_group = completer.group("goto")




@goto_group.action("wikamp")
def _goto_wikamp():
    fh = FirefoxHandler(lambda: quit(1))
    fh.open_wikamp()
    fh.open_website("https://ftims.edu.p.lodz.pl/course/view.php?id=3012")


@goto_group.action("youtube")
def _goto_youtube():
    fh = FirefoxHandler(lambda: quit(1))
    fh.open_website("https://www.youtube.com/")

@completer.action("exit")
@completer.action("quit")
@completer.action("q")
def _exit():
    quit(0)


if __name__ == "__main__":
    logging.basicConfig(filename='myapp.log', level=logging.DEBUG)
    session = PromptSession()

    while True:
        prompt_result = session.prompt("> ", completer=completer, validator=completer.get_validator())
        completer.run_action(prompt_result)
