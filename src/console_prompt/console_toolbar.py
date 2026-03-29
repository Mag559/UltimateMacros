from logging import getLogger
from time import time

import numpy as np
PI_066 = np.pi * 0.66
PI_132 = np.pi * 1.32

def get_color_style(current_time: float) -> str:
    r = int((np.sin(current_time) + 1.0) * 127.5)
    g = int((np.sin(current_time + PI_066) + 1.0) * 127.5)
    b = int((np.sin(current_time + PI_132) + 1.0) * 127.5)

    return f"bg:#{r:02x}{g:02x}{b:02x}"


class ConsoleToolbar:
    def __init__(self, canvas_width: int, canvas_heigh: int):
        self.logger = getLogger(__name__)
        self.toolbar_state = [("bg:#eeeeee", "")]

        self.needs_updating: bool = False
        self.canvas_width = canvas_width
        self.canvas_height = canvas_heigh

        self.canvas = np.full((canvas_heigh, canvas_width), ' ', dtype="<U1")

        self.styles = ["bg:#eeeeee"]
        self.style_canvas = np.full((canvas_heigh, canvas_width), 0, dtype="uint8")


    def get(self):
        if self.needs_updating:
            self.toolbar_state = []

            for style_row, char_row in zip(self.style_canvas, self.canvas):
                # znajdź miejsca, gdzie zmienia się wartość
                changes = np.where(np.diff(style_row) != 0)[0] + 1

                # podziel indeksy na grupy
                indices = np.split(np.arange(len(style_row)), changes)

                # dla każdej grupy zrób join znaków
                row_groups = [(self.styles[style_row[idx[0]]], "".join(char_row[idx])) for idx in indices]

                self.toolbar_state.extend(row_groups)
                self.toolbar_state.append(('', '\n'))




            # for y, row in enumerate(self.canvas):
            #     self.toolbar_state.append(
            #         (
            #             get_color_style(
            #             time() - 2 * np.pi * y / self.canvas_height),
            #             "".join(row) + '\n'
            #         )
            #     )

            # text = '\n'.join("".join(r) for r in self.canvas)
            # self.toolbar_state = [(self.style, text)]
            self.needs_updating = False

        return self.toolbar_state


    def wipe_canvas(self, x: int, y: int, width: int, height: int):
        self.canvas[y:y + height, x:x + width] = ' '
        self.needs_updating = True


    def draw_on_canvas(self, drawing: np.ndarray, x: int, y: int) -> None:
        self.canvas[y:y + drawing.shape[0], x:x + drawing.shape[1]] = drawing
        self.needs_updating = True


    def add_new_style(self, style: str) -> int:
        self.styles.append(style)
        return len(self.styles) - 1


    def update_style(self, new_style: str, style_idx: int):
        if not 0 <= style_idx < len(self.styles):
            raise ValueError(f"Style {style_idx} out of range")
        self.styles[style_idx] = new_style
        self.needs_updating = True


    def draw_style_canvas(self, from_x: int, from_y: int, to_x: int, to_y: int, style_idx: int) -> None:
        if not 0 <= style_idx < len(self.styles):
            raise ValueError(f"Style {style_idx} out of range")
        self.style_canvas[from_y:to_y, from_x:to_x] = style_idx
        self.needs_updating = True