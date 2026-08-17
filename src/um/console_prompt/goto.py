from .console_base import ConsoleBase
import um.base_macro
import um.repeater

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


def _on_firefox_macro_fail():
    raise SystemExit(1)


def setup_goto(console_base: ConsoleBase) -> None:
    """
    Register actions for going to a certain website.
    :param console_base: a bridge to some of the console Main's functionality
    :return:
    """
    goto_group = console_base.completer.group("goto")

    @console_base.default
    def _goto():
        print("Command for opening websites in firefox")

    @goto_group.action("wikamp")
    @console_base.completer.param(list(WIKAMP_SUBJECT_WEBSITES.keys()))
    @console_base.completer.param(None, cast=str)
    def _goto_wikamp(subject: str = ""):
        console_base.focus_release()
        macro_interpreter = um.repeater.InterpreterMacro("wikamp.ins")

        if subject != "":
            macro_interpreter.interpreter.variables["subject"] = WIKAMP_SUBJECT_WEBSITES[subject]

        macro_interpreter.start()

    # @goto_group.action("youtube")
    # def _goto_youtube():
    #     console_base.focus_release()
    #     fh = FirefoxHandler(_on_firefox_macro_fail)
    #     fh.open_website("https://www.youtube.com/")
