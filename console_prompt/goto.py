from .console_base import completer, default
from firefox_handling.wikamp import FirefoxHandler

WIKAMP_SUBJECT_WEBSITES = {
    "posk": "https://ftims.edu.p.lodz.pl/course/view.php?id=3012",
    "kompo": "https://ftims.edu.p.lodz.pl/course/view.php?id=3012",
}

goto_group = completer.group("goto")

@default
def _goto():
    print("Incomplete command.\nDescription:")
    print("Command for opening websites in firefox")


@goto_group.action("wikamp")
@completer.param(["posk", "kompo"])
@completer.param(None)
def _goto_wikamp(subject: str = "", attendance_code: str = ""):
    fh = FirefoxHandler(lambda: quit(1))
    fh.open_wikamp()
    if subject == "":
        return
    fh.open_website(WIKAMP_SUBJECT_WEBSITES[subject])
    if attendance_code != "":
        print("Attendance marking hasn't been implemented yet, sorry")


@goto_group.action("youtube")
def _goto_youtube():
    fh = FirefoxHandler(lambda: quit(1))
    fh.open_website("https://www.youtube.com/")