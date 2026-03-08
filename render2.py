import time

import numpy as np


start = time.time()


def find_axis_breakpoints_squared():
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


    axis_points = np.array([-upper1[1], -right_middle[1], -left_middle[1], -left2[1]])
    for i in range(len(axis_points)):
        axis_points[i] = axis_points[i] ** 2 * np.sign(axis_points[i])

    return axis_points


axis_points = find_axis_breakpoints_squared()


def get_point_on_axis(point_x, point_y, axis_angle) -> float:
    slope = np.tan(axis_angle)

    axis_x = (point_y * slope + point_x) / (slope * slope + 1)
    axis_y = slope * axis_x
    x = axis_x * axis_x + axis_y * axis_y

    if (np.atan2(axis_y, axis_x) - axis_angle) % (np.pi * 2) > 0.1:
        x *= -1
    return x


def get_point_in_3axis_squared(point_x, point_y, rotation: float = 0) -> tuple:
    # -1 * point_y * point_y * np.sign(point_y),(
    return (get_point_on_axis(point_x, point_y, 5 * np.pi / 6 + rotation),
            get_point_on_axis(point_x, point_y, -np.pi / 2 + rotation),
            get_point_on_axis(point_x, point_y, np.pi / 6 + rotation))


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


def draw_polygon_numpy(size, rotation) -> str:
    # Create coordinate grid
    xs = np.linspace(-1, 1, size * 2)
    ys = np.linspace(1, -1, size)
    # X, Y = np.meshgrid(xs, ys)

    # canvas = np.full((size, 2 * size), " ", dtype="<U1")
    drawing = ""
    for y in ys:
        for x in xs:
            x2, y2, z2 = get_point_in_3axis_squared(x, y, rotation)
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

    return drawing


# for rotation in np.linspace(0, 2 * np.pi, 50):
#     draw_polygon_numpy(30)
#     time.sleep(0.1)
#
# # rotation = 0
# draw_polygon_numpy(30)
#
# print(time.time() - start)