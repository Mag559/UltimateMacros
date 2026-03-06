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

# print(points)
import numpy as np


axis_points = [-upper1[1], -right_middle[1], -left_middle[1], -left2[1]]


def get_point_in_3axis(point_x, point_y) -> tuple:
    x_axis_a = np.tan(150. / 180 * np.pi)
    z_axis_a = np.tan(30. / 180 * np.pi)

    x_axis_x = (point_y * x_axis_a + point_x) / (x_axis_a * x_axis_a + 1)
    x_axis_y = x_axis_a * x_axis_x
    x = np.sqrt(x_axis_x * x_axis_x + x_axis_y * x_axis_y)
    if x_axis_x > 0:
        x *= -1

    z_axis_x = (point_y * z_axis_a + point_x) / (z_axis_a * z_axis_a + 1)
    z_axis_y = z_axis_a * z_axis_x
    z = np.sqrt(z_axis_x * z_axis_x + z_axis_y * z_axis_y)
    if z_axis_x < 0:
        z *= -1

    return x, -point_y, z


def get_colour(xi, yi, zi) -> str:
    black = "."
    gray = "*"
    white = "#"
    match xi, yi, zi:
        case 0, 2, 2:
            return black
        case 2, 0, 2:
            return white
        case 2, 2, 0:
            return gray

        case _, _, 2:
            return white
        case 2, _, _:
            return gray
        case _, 2, _:
            return black

        case 1, 0, 1:
            return gray
        case 0, 1, 1:
            return white
        case 1, 1, 0:
            return black

        case 1, _, _:
            return black
        case _, _, 1:
            return gray

        case _, 1, _:
            return white

        case _:
            return ' '


def draw_polygon_numpy(size=10):
    # Create coordinate grid
    xs = np.linspace(-1, 1, size * 2)
    ys = np.linspace(1, -1, size)
    # X, Y = np.meshgrid(xs, ys)

    # canvas = np.full((size, 2 * size), " ", dtype="<U1")
    drawing = ""
    for y in ys:
        for x in xs:
            x2, y2, z2 = get_point_in_3axis(x, y)
            integer_cords = [0, 0, 0]
            for axis_coord, integer_coord in zip((x2, y2, z2), range(3)):
                if axis_coord < axis_points[0]:
                    break

                for i, point in enumerate(axis_points[:-1]):
                    if point <= axis_coord <= axis_points[i + 1]:
                        integer_cords[integer_coord] = i

                if axis_coord > axis_points[-1]:
                    break

            else:
                drawing += get_colour(*integer_cords)
                continue
            drawing += ' '

        drawing += "\n"

    print(drawing)

# for s in range(10, 30):
draw_polygon_numpy(30)
