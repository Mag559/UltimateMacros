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
        self.toolbar_state = [("bg:#eeeeee", "")]

        self.needs_updating: bool = False
        self.canvas_width = canvas_width
        self.canvas_height = canvas_heigh

        self.canvas = np.full((canvas_heigh, canvas_width), ' ', dtype="<U1")

        self.style = "bg:#eeeeee"


    def get(self):
        if self.needs_updating:
            self.toolbar_state = []
            for y, row in enumerate(self.canvas):
                self.toolbar_state.append(
                    (
                        get_color_style(
                        time() - 2 * np.pi * y / self.canvas_height),
                        "".join(row) + '\n'
                    )
                )

            # text = '\n'.join("".join(r) for r in self.canvas)
            # self.toolbar_state = [(self.style, text)]
            self.needs_updating = False

        return self.toolbar_state


    def wipe(self, x: int, y: int, width: int, height: int):
        self.canvas[y:y + height, x:x + width] = ' '
        self.needs_updating = True


    def update(self, drawing: np.ndarray, x: int, y: int) -> None:
        self.canvas[y:y + drawing.shape[0], x:x + drawing.shape[1]] = drawing

        self.needs_updating = True

    # def update(self, block_x: int, block_y: int, text: str, style: str = ""):
    #     self.toolbar_blocks[block_y][block_x] = (style, text)
    #     self.needs_updating = True

    def set_style(self, style: str):
        self.style = style
        self.needs_updating = True


def horizontally_join(*blocks, height:int = 20):
    """
    Requires blocks to have consistent width in every line.
    Blocks can end early, however they must have at least one line, to gauge their width
    every block in blocks: ("text style", text)
    result: [("text style", text), ...]
    """
    result = []
    styles = [style for style, text in blocks]
    lines = [[line for line in text.split("\n")] for style, text in blocks]
    widths = [len(block_lines[0]) * ' ' for block_lines in lines]

    empty_block_ids = []
    for row in range(height):
        for block_i in range(len(blocks)):
            if len(lines[block_i]) <= row:
                # there isn't a line for this row in this block
                # mark it as empty
                empty_block_ids.append(block_i)

            if block_i in empty_block_ids:
                # if it's empty add the appropriate space count with default style
                result.append(("", widths[block_i]))
                continue

            # if len(empty_block_ids) == len(blocks) - 1:
            #     # if there's only one of the blocks left, there is no point sending it in separately styled chunks
            #     result.append(
            #         (styles[block_i],
            #          ),
            #     )
            result.append((styles[block_i], lines[block_i][row]))
        result.append(("", '\n'))

    return result
