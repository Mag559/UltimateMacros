from logging import getLogger
import numpy as np

from um.profiles import ProfileReader


class ConsoleToolbar:
    def __init__(self, canvas_width: int, canvas_heigh: int):
        self.logger = getLogger(__name__)
        self.toolbar_state = [(ProfileReader.profile().console_toolbar_style, "")]

        self.state_needs_updating: bool = False
        self.style_indices_need_updating: bool = True

        self.canvas_width = canvas_width
        self.canvas_height = canvas_heigh

        self.canvas = np.full((canvas_heigh, canvas_width), ' ', dtype="<U1")

        self.styles = [ProfileReader.profile().console_toolbar_style]
        self.style_canvas = np.full((canvas_heigh, canvas_width), 0, dtype="uint8")

        self.indices: list = [[] for _ in range(canvas_heigh)]

    def get(self):
        if self.style_indices_need_updating:
            self.update_style_indices()

        if self.state_needs_updating:
            self.update_toolbar_state()

        return self.toolbar_state

    def update_toolbar_state(self):
        self.toolbar_state = []

        for row_idx, char_row in enumerate(self.canvas):
            # join individual characters in each group
            row_groups = [
                (
                    self.styles[self.style_canvas[row_idx, idx[0]]],
                    "".join(char_row[idx])
                ) for idx in self.indices[row_idx]
            ]

            self.toolbar_state.extend(row_groups)
            self.toolbar_state.append(('', '\n'))

        self.state_needs_updating = False

    def update_style_indices(self):
        for row_idx, style_row in enumerate(self.style_canvas):
            # find places where style index changes
            changes = np.where(np.diff(style_row) != 0)[0] + 1

            # split all the indexes in the row into groups with the same style
            self.indices[row_idx] = np.split(np.arange(len(style_row)), changes)

        self.style_indices_need_updating = False
        self.state_needs_updating = True

    def wipe_canvas(self, x: int, y: int, width: int, height: int):
        self.canvas[y:y + height, x:x + width] = ' '
        self.state_needs_updating = True

    def draw_on_canvas(self, drawing: np.ndarray, x: int, y: int) -> None:
        self.canvas[y:y + drawing.shape[0], x:x + drawing.shape[1]] = drawing
        self.state_needs_updating = True

    def add_new_style(self, style: str) -> int:
        self.styles.append(style)
        return len(self.styles) - 1

    def update_style(self, new_style: str, style_idx: int):
        if not 0 <= style_idx < len(self.styles):
            raise ValueError(f"Style {style_idx} out of range")
        self.styles[style_idx] = new_style
        self.state_needs_updating = True

    def draw_style_canvas(self, from_x: int, from_y: int, to_x: int, to_y: int, style_idx: int) -> None:
        if not 0 <= style_idx < len(self.styles):
            raise ValueError(f"Style {style_idx} out of range")
        self.style_canvas[from_y:to_y, from_x:to_x] = style_idx
        self.style_indices_need_updating = True
        self.state_needs_updating = True
