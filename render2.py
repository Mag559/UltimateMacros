import time

import numpy as np


# Parameters
a = 0.2
mirror_Y_axis = np.array([[-1.0, 0.0],
                          [ 0.0, 1.0]])

upper1 = np.array([np.sin(-a), np.cos(a)])

upper2 = upper1 @ mirror_Y_axis

# transposed rotation matrix
ph = 2.0/3.0 * np.pi
rotation120 = np.array([[np.cos(ph), np.sin(ph)],
              [-np.sin(ph),  np.cos(ph)]])

# left / right points
left2 = upper1 @ rotation120
left1 = upper2 @ rotation120

right1 = left1 @ mirror_Y_axis
right2 = left2 @ mirror_Y_axis

# weighted middles
weight = 0.67
upper_middle = (1 - weight) * left2 + weight * upper2
left_middle  = (1 - weight) * right1 + weight * left1
right_middle = (1 - weight) * upper1 + weight * right2

# centers
center_right = np.array([
    (right_middle[1] - upper_middle[1]) / np.tan(ph) + upper_middle[0],
    right_middle[1]
])

center_upper  = center_right @ rotation120
center_left = center_upper  @ rotation120

# Optional: print results
points = {
    'upper1': upper1,
    'upper2': upper2,
    'left1': left1,
    'left2': left2,
    'right1': right1,
    'right2': right2,
    'upper_middle': upper_middle,
    'left_middle': left_middle,
    'right_middle': right_middle,
    'center_right': center_right,
    'center_left': center_left,
    'center_upper': center_upper
}

import numpy as np

def point_in_polygon_vectorized(x, y, vertices):
    """
    x, y: 2D arrays
    vertices: list of (x, y)
    returns: boolean mask of points inside polygon
    """
    vertices = np.array(vertices)
    x1 = vertices[:, 0]
    y1 = vertices[:, 1]
    x2 = np.roll(x1, -1)
    y2 = np.roll(y1, -1)

    inside = np.zeros_like(x, dtype=bool)

    for i in range(len(vertices)):
        cond = ((y1[i] > y) != (y2[i] > y)) & (
            x < (x2[i] - x1[i]) * (y - y1[i]) / (y2[i] - y1[i] + 1e-12) + x1[i]
        )
        inside ^= cond

    return inside


def draw_polygon_numpy(size=30, *vertice_sets):
    # Create coordinate grid
    xs = np.linspace(-1, 1, 2 * size)
    ys = np.linspace(1, -1, size)
    X, Y = np.meshgrid(xs, ys)

    canvas = np.full((size, 2 * size), " ", dtype="<U1")

    for char, vertices in zip(["*", ".", "#"], vertice_sets):
        mask = point_in_polygon_vectorized(X, Y, vertices)
        canvas[mask] = char

    print("\n".join("".join(row) for row in canvas))

for s in range(10, 30):
    draw_polygon_numpy(s,
                       [left1, left2, upper_middle, center_right, right_middle, upper1],
                       [upper1, right_middle, center_left, left_middle, right1, upper2],
                       [right2, left2, upper_middle, center_upper, left_middle, right1]
                       )
