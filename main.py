from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter

completer = WordCompleter(
    ["load", "save", "exit", "help"],
    ignore_case=True
)

session = PromptSession()

while True:
    text = session.prompt("> ", completer=completer)
    print("You typed:", text)
