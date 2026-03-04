import dataclasses
from math import cos, sin
from time import sleep

import numpy as np

SCREEN_X = 100
SCREEN_Y = 15

@dataclasses.dataclass
class RenderedPoint:
    z: float = 1000
    char: str = ' '


screen = np.empty((SCREEN_X, SCREEN_Y), dtype=RenderedPoint)

def reset_screen() -> None:
    screen.fill(RenderedPoint())


def render_on_screen(point: RenderedPoint, x: float, y: float) -> None:
    screen_x = int(x + SCREEN_X / 2)
    screen_y = int(y + SCREEN_Y / 2)
    if not (0 <= screen_x < SCREEN_X and 0 <= screen_y < SCREEN_Y):
        return

    if point.z > screen[screen_x, screen_y].z:
        return

    screen[screen_x, screen_y] = point


def render_screen() -> None:
    for y in range(SCREEN_Y):
        for x in range(SCREEN_X):
            print(screen[x, y].char, end='')
        print()


def rotate_point(x, y, z, angle_z, angle_y, angle_x):
    sin_z = sin(angle_z)
    cos_z = cos(angle_z)
    sin_y = sin(angle_y)
    cos_y = cos(angle_y)
    sin_x = sin(angle_x)
    cos_x = cos(angle_x)
    return (cos_z * cos_y) * x + (cos_z * sin_y * sin_x - sin_z * cos_x) * y + (cos_z * sin_y * cos_x + sin_z * sin_x) * z, \
        (sin_z * cos_y) * x + (sin_z * sin_y * sin_x + cos_z * cos_x) * y + (sin_z * sin_y * cos_x - cos_z * sin_x) * z, \
        (-sin_y) * x + (cos_y * sin_x) * y + (cos_y * cos_x) * z



def main() -> None:
    rotation = 0
    while True:
        reset_screen()
        for x in range(-5, 5):
            for y in range(-5, 5):
                for z in range(-5, 5):
                    if x == 4:
                        char = '.'
                    elif x == -5:
                        char = '|'
                    elif y == 4:
                        char = '-'
                    elif y == -5:
                        char = '&'
                    elif z == 4:
                        char = '|'
                    else:
                        char = '['
                    x2, y2, z2 = rotate_point(x, y, z, 0, rotation, 0)
                    render_on_screen(RenderedPoint(z2, char), x2, y2)

        render_screen()
        sleep(.3)
        rotation += 0.04



if __name__ == '__main__':
    main()