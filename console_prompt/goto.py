from time import sleep

from base_macro import InputPresser
from .console_base import completer, default
from firefox_handling.wikamp import FirefoxHandler

WIKAMP_SUBJECT_WEBSITES = {
    "tips": "https://ftims.edu.p.lodz.pl/course/view.php?id=2206",
    "wspolbiegi": "https://ftims.edu.p.lodz.pl/course/view.php?id=2332",
    "wbudy": "https://ftims.edu.p.lodz.pl/course/view.php?id=3094",
    "grafika": "https://ftims.edu.p.lodz.pl/course/view.php?id=8",
    "kryptografia": "https://ftims.edu.p.lodz.pl/course/view.php?id=1801",
    "numerki": "https://ftims.edu.p.lodz.pl/course/view.php?id=34"
}

WIKAMP_ATTENDANCE_WEBSITES = {
    "grafika": "https://ftims.edu.p.lodz.pl/mod/attendance/view.php?id=115194"
}

goto_group = completer.group("goto")

@default
def _goto():
    print("Incomplete command.\nDescription:")
    print("Command for opening websites in firefox")


@goto_group.action("wikamp")
@completer.param(list(WIKAMP_SUBJECT_WEBSITES.keys()))
@completer.param(None, cast=str)
def _goto_wikamp(subject: str = "", attendance_code: str = ""):
    fh = FirefoxHandler(lambda: quit(1))
    fh.open_wikamp()
    if subject == "":
        return
    fh.open_website(WIKAMP_SUBJECT_WEBSITES[subject])

    if attendance_code == "":
        return

    if subject not in WIKAMP_ATTENDANCE_WEBSITES.keys():
        print("Attendance has not been configured for this subject")

    fh.wait_for_firefox_loading_wheel()
    fh.open_website(WIKAMP_ATTENDANCE_WEBSITES[subject])
    fh.wait_for_firefox_loading_wheel()
    InputPresser.move_mouse((1000, 800)) # move slightly up for the cursor to hover over the website

    sleep(1.5)
    InputPresser.scroll(-5)

    fh.press_register_attendance()

    InputPresser.move_mouse((687, 595))
    InputPresser.left_click()

    InputPresser.input_string(attendance_code)
    InputPresser.tab()
    InputPresser.tap(' ')
    InputPresser.enter()



@goto_group.action("youtube")
def _goto_youtube():
    fh = FirefoxHandler(lambda: quit(1))
    fh.open_website("https://www.youtube.com/")