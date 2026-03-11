import time

import numpy as np


start = time.time()


def find_axis_breakpoints():
    # Parameters
    a = 0.2
    mirror_y_axis = np.array([[-1.0, 0.0],
                              [ 0.0, 1.0]])

    upper1 = np.array([np.sin(-a), np.cos(a)])

    upper2 = upper1 @ mirror_y_axis

    # transposed rotation matrix
    ph = 2.0/3.0 * np.pi
    rotation120 = np.array([[np.cos(ph), np.sin(ph)],
                  [-np.sin(ph),  np.cos(ph)]])

    # left / right points
    left2 = upper1 @ rotation120
    left1 = upper2 @ rotation120

    right1 = left1 @ mirror_y_axis
    right2 = left2 @ mirror_y_axis

    # weighted middles
    weight = 0.67
    left_middle  = (1 - weight) * right1 + weight * left1
    right_middle = (1 - weight) * upper1 + weight * right2


    return np.array([-10000, -upper1[1], -right_middle[1], -left_middle[1], -left2[1], 10000])


axis_points = find_axis_breakpoints()


colour_map = np.full((6,6,6), ' ', dtype='<U1')
colour_map[2, 4, 4] = '.'
colour_map[4, 2, 4] = '#'
colour_map[4, 4, 2] = '*'
colour_map[2, 2, 4] = '#'
colour_map[2, 3, 4] = '#'
colour_map[3, 2, 4] = '#'
colour_map[4, 2, 2] = '*'
colour_map[4, 3, 2] = '*'
colour_map[2, 4, 2] = '.'
colour_map[2, 4, 3] = '.'
colour_map[3, 4, 2] = '.'
colour_map[3, 2, 3] = '*'
colour_map[3, 3, 2] = '.'
colour_map[2, 2, 3] = '*'
colour_map[4, 2, 3] = '*'
colour_map[3, 2, 2] = '.'
colour_map[2, 3, 2] = '#'
colour_map[2, 3, 3] = '#'



def draw_polygon_numpy(size, rotation) -> str:
    # Create coordinate grid
    xs = np.linspace(-1, 1, size * 2)
    ys = np.linspace(1, -1, size)
    X, Y = np.meshgrid(xs, ys)

    pts = np.stack([X, Y], axis=-1)

    axes = np.array([
        5 * np.pi / 6,
        -np.pi / 2,
        np.pi / 6
    ]) + rotation

    dirs = np.stack([np.cos(axes), np.sin(axes)], axis=1)

    proj = pts @ dirs.T

    bins = np.digitize(proj, axis_points)

    canvas = np.full((size, 2 * size), ' ', dtype='<U1')

    for i in range(size):
        for j in range(2 * size):
            canvas[i, j] = colour_map[bins[i, j][0], bins[i, j][1], bins[i, j][2]]

    return "\n".join("".join(r) for r in canvas)



# for rotation in np.linspace(0, 2 * np.pi, 50):
#     draw_polygon_numpy(30)
#     time.sleep(0.1)
#
# # rotation = 0
# draw_polygon_numpy(30)
#
# print(time.time() - start)