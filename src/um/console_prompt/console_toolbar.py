from logging import getLogger
import numpy as np

from um.profiles import ProfileReader


TOOLBAR_STATE = list[tuple[str, str]]


class ConsoleToolbar:
    """
    Class responsible for tying together styles and ascii drawings,
    keeping track of the current canvas state
    to communicate them to prompt toolkit.
    """
    def __init__(self, canvas_width: int, canvas_heigh: int):
        """

        :param canvas_width: how many characters should be expected to fit in the window size per row
        :param canvas_heigh: how many rows of characters should be expected to fit in the window size
        """
        self.logger = getLogger(__name__)
        self.toolbar_state: TOOLBAR_STATE = [(ProfileReader.profile().console_toolbar_style, "")]

        self.state_needs_updating: bool = False
        self.style_indices_need_updating: bool = True

        self.canvas_width: int = canvas_width
        self.canvas_height: int = canvas_heigh

        self.canvas: np.ndarray = np.full((canvas_heigh, canvas_width), ' ', dtype="<U1")

        self.styles: list[str] = [ProfileReader.profile().console_toolbar_style]
        self.style_canvas: np.ndarray = np.full((canvas_heigh, canvas_width), 0, dtype="uint8")

        self.indices: list = [[] for _ in range(canvas_heigh)]

    def get(self) -> TOOLBAR_STATE:
        """
        Bulk resolve any updates since the last call
        and return the details on how the toolbar should look like
        :return: details on how the toolbar should look like, ready to be fed to prompt toolkit
        """
        if self.style_indices_need_updating:
            self.update_style_indices()

        if self.state_needs_updating:
            self.update_toolbar_state()

        return self.toolbar_state

    def update_toolbar_state(self) -> None:
        """
        Group characters with the same style according to known style indices
        creating the current toolbar state.
        :return:
        """
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

    def update_style_indices(self) -> None:
        """
        Find positions within each row of characters where the style changes
        and store that information in ``self.indices``.
        Styles shift significantly less often than displayed characters,
        hence the separation into update style and update state.
        :return:
        """
        for row_idx, style_row in enumerate(self.style_canvas):
            # find places where style index changes
            changes = np.where(np.diff(style_row) != 0)[0] + 1

            # split all the indexes in the row into groups with the same style
            self.indices[row_idx] = np.split(np.arange(len(style_row)), changes)

        self.style_indices_need_updating = False
        self.state_needs_updating = True

    def wipe_canvas(self, x: int, y: int, width: int, height: int) -> None:
        """
        Completely clear a section of the canvas
        by setting the characters to `space`
        :param x: from which column
        :param y: from which row
        :param width: how many columns
        :param height: how many rows
        :return:
        """
        self.canvas[y:y + height, x:x + width] = ' '
        self.state_needs_updating = True

    def draw_on_canvas(self, drawing: np.ndarray, x: int, y: int) -> None:
        """
        Replace a section of the canvas with the supplied drawing.
        :raises IndexError: if drawing would extend past the canvas.
        :param drawing: numpy 2D character array to be drawn
        :param x: where should the drawing's left edge be
        :param y: where should the drawing's top edge be
        :return:
        """
        self.canvas[y:y + drawing.shape[0], x:x + drawing.shape[1]] = drawing
        self.state_needs_updating = True

    def add_new_style(self, style: str) -> int:
        """
        Register a new style.
        :param style: prompt toolkit style specifying string `"fg:#aabbcc"`
        :return: ID of the created style
        """
        self.styles.append(style)
        return len(self.styles) - 1

    def update_style(self, new_style: str, style_idx: int) -> None:
        """
        Update a registered style (usually change the colour).
        :param new_style: new prompt toolkit style specifying string `"fg:#aabbcc"`
        :param style_idx: style identifier
        :return:
        :raises ValueError: if there is no style of the specified identifier
        """
        if not 0 <= style_idx < len(self.styles):
            raise ValueError(f"Style {style_idx} out of range")
        self.styles[style_idx] = new_style
        self.state_needs_updating = True

    def draw_style_canvas(self, from_x: int, from_y: int, to_x: int, to_y: int, style_idx: int) -> None:
        """
        Specify a section of the canvas to have a certain style.
        As it happens less often than updating the characters (usually once per use case of the class),
        it is separate from updating the drawing in ``self.draw_on_canvas``.
        :param from_x: from which column
        :param from_y: from which row
        :param to_x: to which column
        :param to_y: to which row
        :param style_idx: identifier of the style
        :return:
        """
        if not 0 <= style_idx < len(self.styles):
            raise ValueError(f"Style {style_idx} out of range")
        self.style_canvas[from_y:to_y, from_x:to_x] = style_idx
        self.style_indices_need_updating = True
        self.state_needs_updating = True
