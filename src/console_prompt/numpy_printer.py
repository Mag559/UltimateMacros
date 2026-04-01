import numpy as np


class NumpyPrinter:
    def __init__(self, max_width: int = 40, max_height: int = 20) -> None:
        self.canvas = np.full((max_height, max_width), ' ', dtype="<U1")
        self.max_width = max_width
        self.max_height = max_height
        self.line = 0


    def print(self, text: str):
        if self.line >= self.max_height:
            return
        self.canvas[self.line, 0:min(len(text), self.max_width)] = list(text)[:self.max_width]
        self.line = self.line + 1


    def get_drawing(self) -> np.ndarray:
        return self.canvas

