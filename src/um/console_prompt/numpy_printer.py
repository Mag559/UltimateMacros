import numpy as np


class NumpyPrinter:
    """
    Helper class to turn lines of text into a numpy 2D array.
    """
    def __init__(self, max_width: int = 40, max_height: int = 20) -> None:
        """

        :param max_width: up to how many characters each line should be
        :param max_height: how many lines should be at most
        """
        self.canvas = np.full((max_height, max_width), ' ', dtype="<U1")
        self.max_width = max_width
        self.max_height = max_height
        self.line = 0

    def print(self, text: str) -> None:
        """
        Add the next line of text to the canvas.
        If there are no more free lines, does nothing.
        If the text is too long, it's end is cut.
        :param text: a line of text to print
        :return:
        """
        if self.line >= self.max_height:
            return
        self.canvas[self.line, 0:min(len(text), self.max_width)] = list(text)[:self.max_width]
        self.line = self.line + 1

    def get_drawing(self) -> np.ndarray:
        """
        Get the ready drawing.
        :return: array of rows of "<U1" characters
        """
        return self.canvas
