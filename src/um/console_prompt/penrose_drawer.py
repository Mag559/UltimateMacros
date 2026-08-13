import numpy as np


class PenroseDrawer:
    """
    Dedicated class for drawing a spinny penrose triangle with ascii characters: `.`, `*` and `#`.
    Runs on the assumption that these characters have constant size (i.e. m isn't wider than i)
    and they are approximately twice as tall as they are wide
    """
    def __init__(self, size: int):
        """

        :param size: how many characters high should the drawing be
        """
        self.axis_breakpoints: np.ndarray = PenroseDrawer.find_axis_breakpoints()
        self.colour_map: np.ndarray = np.full((6, 6, 6), ' ', dtype='<U1')
        self.fill_colour_map()

        # Create coordinate grid
        self.width: int = 2 * size
        self.height: int = size
        xs = np.linspace(-1, 1, self.width)
        ys = np.linspace(1, -1, self.height)

        self.pts = np.stack(np.meshgrid(xs, ys), axis=-1)

    def draw(self, rotation: float) -> np.ndarray:
        """
        Optimized with the help of AI main method for computing the drawing at a set rotation.
        For a matrix of points:
        computes orthographic projections onto 3 axis - up_left, down and up_right,
        finds between which two precomputed breakpoints each point lies (on each axis)
        and uses a lookup table to determine the ascii character.
        :param rotation: rotation of the drawing, in radians, counterclockwise
        :return: numpy two-dimensional ndarray of '<U1' characters, array of rows of characters
        """
        axes = np.array([
            5 * np.pi / 6,
            -np.pi / 2,
            np.pi / 6
        ]) + rotation

        dirs = np.stack([np.cos(axes), np.sin(axes)], axis=1)

        proj = self.pts @ dirs.T

        bins = np.digitize(proj, self.axis_breakpoints)

        return self.colour_map[bins[..., 0], bins[..., 1], bins[..., 2]]

    def fill_colour_map(self) -> None:
        """
        Fill the lookup table with characters designated for each section of the triangle,
        traditionally `.`, `*` and `#`, however this can be changed at no risk
        :return:
        """
        # corners
        self.colour_map[2, 4, 4] = '.'
        self.colour_map[4, 4, 2] = '*'
        self.colour_map[4, 2, 4] = '#'

        # big edges
        self.colour_map[2, 2, 4] = '#'
        self.colour_map[4, 2, 2] = '*'
        self.colour_map[2, 4, 2] = '.'

        # tight lines around corners
        self.colour_map[2, 3, 4] = '#'
        self.colour_map[3, 2, 4] = '#'
        self.colour_map[4, 3, 2] = '*'
        self.colour_map[4, 2, 3] = '*'
        self.colour_map[2, 4, 3] = '.'
        self.colour_map[3, 4, 2] = '.'

        # inner diamonds
        self.colour_map[3, 2, 3] = '*'
        self.colour_map[3, 3, 2] = '.'
        self.colour_map[2, 3, 3] = '#'

        # inner edges
        self.colour_map[3, 2, 2] = '.'
        self.colour_map[2, 2, 3] = '*'
        self.colour_map[2, 3, 2] = '#'

    @staticmethod
    def find_axis_breakpoints() -> np.ndarray:
        """
        Mathematically find points, where an edge of the triangle cross an axis.
        Applicable to all axis due to symmetry.
        Unoptimized, however runs only once in the constructor.
        :return: numpy 1D array of breakpoints
        """
        # Parameters
        outer_spread = 0.2
        inner_spread = 0.67

        mirror_y_axis = np.array([[-1.0, 0.0],
                                  [0.0, 1.0]])

        upper1 = np.array([np.sin(-outer_spread), np.cos(outer_spread)])

        upper2 = upper1 @ mirror_y_axis

        # transposed rotation matrix
        ph = 2.0 / 3.0 * np.pi
        rotation120 = np.array([[np.cos(ph), np.sin(ph)],
                                [-np.sin(ph), np.cos(ph)]])

        # left / right points
        left2 = upper1 @ rotation120
        left1 = upper2 @ rotation120

        right1 = left1 @ mirror_y_axis
        right2 = left2 @ mirror_y_axis

        left_middle = (1 - inner_spread) * right1 + inner_spread * left1
        right_middle = (1 - inner_spread) * upper1 + inner_spread * right2

        return np.array([-10000, -upper1[1], -right_middle[1], -left_middle[1], -left2[1], 10000])
