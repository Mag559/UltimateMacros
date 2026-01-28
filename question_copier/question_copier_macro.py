import re
from enum import Enum
from functools import reduce
from pathlib import Path
from time import sleep

import pyperclip

from base_macro.base_macro import BaseMacro
from base_macro.input_collector import ImportantEvents


class State(Enum):
    READING_QUESTION = 0
    READING_ANSWERS = 1


class QuestionCopier(BaseMacro):
    """
    Select question + copy
    Select answer + copy
    If it was a correct answer, press RIGHT CLICK (and again to reverse)

    After all the answers, SHORTCUT2
    """
    def __init__(self, file: Path, completely_remove_newlines: bool = False):
        self.completely_remove_newlines = completely_remove_newlines
        self.questions_file = open(file, "a", encoding="utf-8")
        self.state: State = State.READING_QUESTION

        self.question: str = ""
        self.answers: list[str] = []
        self.are_answers_correct: list[bool] = []

        super().__init__()

    def update(self, event_code: ImportantEvents):
        super().update(event_code)

        match event_code:
            case ImportantEvents.COPY:
                # read question or answer
                if pyperclip.paste() == "":
                    for i in range(10):
                        if pyperclip.paste() != "":
                            break
                        sleep(0.1)
                    else:
                        print(f"Copying failed at question {self.question}")
                match self.state:
                    case State.READING_QUESTION:
                        self.question = self.replace_newlines(pyperclip.paste())
                        self.state = State.READING_ANSWERS
                    case State.READING_ANSWERS:
                        answer = self.replace_newlines(pyperclip.paste())

                        # remove the accidentally copied `a. `
                        answer = re.sub(r"^[a-z]\.? ", "", answer)
                        self.answers.append(answer)
                        self.are_answers_correct.append(False)
            case ImportantEvents.SHORTCUT2:
                # save question and answers to the file
                self.state = State.READING_QUESTION
                self.write_question_to_file()

                self.question = ""
                self.answers = []
                self.are_answers_correct = []
            case ImportantEvents.RIGHT_CLICK:
                # mark last question as correct
                if len(self.answers) == 0:
                    return
                self.are_answers_correct[-1] = not self.are_answers_correct[-1]


    def write_question_to_file(self):
        question_type = self.deduce_question_type()
        self.questions_file.writelines((
            question_type + "\n",
            self.question + "\n"
        ))


        if question_type == "TF":
            match self.convert_answer_to_bool(self.answers[0]):
                case True:
                    self.questions_file.write("1\n")
                case False:
                    self.questions_file.write("0\n")
                case _:
                    raise Exception("This should not happen")
        else:
            for correct, answer in zip(self.are_answers_correct, self.answers):
                self.questions_file.write("+" * int(correct) + answer + "\n")

        self.questions_file.write("\n")

    @staticmethod
    def convert_answer_to_bool(answer: str) -> bool | None:
        """
        Yes adjacent -> True
        No adjacent -> False
        Doesn't match -> None
        """
        if answer.lower() in ("true", "yes", "prawda", "tak"):
            return True
        if answer.lower() in ("false", "no", "fałsz", "nie"):
            return False
        return None


    def replace_newlines(self, string: str) -> str:
        if self.completely_remove_newlines:
            return re.sub(r"\r?\n", " ", string)

        return re.sub(r"\r?\n", "\\\\n", string)


    def deduce_question_type(self) -> str:
        """
        Detecting question type:
        - only one answer matching one of the `True` presets -> true or false
        - no questions marked as correct -> open
        - one or more questions marked as correct -> multiple choice

        no way to tell multiple choice from single choice for questions with one correct answer
        -> macro always assumes multiple choice since it's probably more common
        """
        if len(self.answers) == 1:
            if self.convert_answer_to_bool(self.answers[0]) is not None:
                return "TF"

        if reduce(
                lambda carry, element: carry and element == False,
                self.are_answers_correct,
                True
        ):
            return "OPEN"

        return "MULTIPLE_CHOICE"


    def terminate(self):
        self.questions_file.close()
        super().terminate()


if __name__ == "__main__":
    QuestionCopier(Path("nat.txt"), completely_remove_newlines=True)