import numpy as np


class PenroseDrawer:
    def __init__(self, size):
        self.axis_breakpoints = PenroseDrawer.find_axis_breakpoints()
        self.colour_map = np.full((6, 6, 6), ' ', dtype='<U1')
        self.fill_colour_map()
        # Create coordinate grid
        xs = np.linspace(-1, 1, size * 2)
        ys = np.linspace(1, -1, size)

        self.pts = np.stack(np.meshgrid(xs, ys), axis=-1)
        self.indent = ' ' * 39


    def draw(self, rotation) -> str:
        axes = np.array([
            5 * np.pi / 6,
            -np.pi / 2,
            np.pi / 6
        ]) + rotation

        dirs = np.stack([np.cos(axes), np.sin(axes)], axis=1)

        proj = self.pts @ dirs.T

        bins = np.digitize(proj, self.axis_breakpoints)

        canvas = self.colour_map[bins[..., 0], bins[..., 1], bins[..., 2]]

        return self.indent + f"\n{self.indent}".join("".join(r) for r in canvas)


    def fill_colour_map(self):
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
    def find_axis_breakpoints():
        # unoptimized function, but runs only once, so its fine
        # Parameters
        a = 0.2
        mirror_y_axis = np.array([[-1.0, 0.0],
                                  [0.0, 1.0]])

        upper1 = np.array([np.sin(-a), np.cos(a)])

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

        # weighted middles
        weight = 0.67
        left_middle = (1 - weight) * right1 + weight * left1
        right_middle = (1 - weight) * upper1 + weight * right2

        return np.array([-10000, -upper1[1], -right_middle[1], -left_middle[1], -left2[1], 10000])

