import asyncio
from collections.abc import Callable
from enum import Enum
from math import sin, pi
from random import randint

from um.profiles import ProfileReader
from um.console_prompt.console_time_keeper import TimeKeeper
from um.console_prompt.console_toolbar import ConsoleToolbar
from um.console_prompt.penrose_drawer import PenroseDrawer


PI_066 = pi * 0.66
PI_132 = pi * 1.32

def get_color_style(current_time: float) -> str:
    r = int((sin(current_time) + 1.0) * 127.5)
    g = int((sin(current_time + PI_066) + 1.0) * 127.5)
    b = int((sin(current_time + PI_132) + 1.0) * 127.5)

    return f"fg:#{r:02x}{g:02x}{b:02x}"

LEFT = ProfileReader.profile().console_toolbar_width // 2 - ProfileReader.profile().console_penrose_size
RIGHT = LEFT + 2 * ProfileReader.profile().console_penrose_size
TOP = 0
BOTTOM = ProfileReader.profile().console_penrose_size


class ConsoleDrawerStyle(Enum):
    RGB = 0
    MONO = 1
    RANDOM_STATIC = 2


class ConsoleDrawer:
    def __init__(self, toolbar: ConsoleToolbar, update_drawing: Callable[[], None], time_keeper: TimeKeeper) -> None:
        self.time_keeper = time_keeper
        self.update_drawing = update_drawing
        self.toolbar = toolbar


        match ConsoleDrawerStyle(ProfileReader.profile().console_penrose_style):
            case ConsoleDrawerStyle.RGB:
                self.initialize_styles: Callable[[], list[int]] = self.initialize_rgb_styles
                self.update_styles: Callable[[list[int]], None] = self.update_rgb_styles
            case ConsoleDrawerStyle.MONO:
                self.initialize_styles: Callable[[], list[int]] = self.initialize_mono_styles
                self.update_styles: Callable[[list[int]], None] = self.update_mono_style
            case ConsoleDrawerStyle.RANDOM_STATIC:
                self.initialize_styles: Callable[[], list[int]] = self.initialize_random_static_style
                self.update_styles: Callable[[list[int]], None] = self.update_random_static_style


    async def spin(self):
        angle: float = ProfileReader.profile().console_penrose_starting_angle
        drawer = PenroseDrawer(ProfileReader.profile().console_penrose_size)


        style_indexes: list[int] = self.initialize_styles()

        while True:
            await asyncio.sleep(ProfileReader.profile().console_penrose_spf)

            await self.time_keeper.drawing_sleep_if_unfocused()

            angle += ProfileReader.profile().console_penrose_spf \
                     * ProfileReader.profile().console_penrose_rotation_speed
            penrose_drawing = drawer.draw(angle)

            self.update_styles(style_indexes)

            self.toolbar.draw_on_canvas(penrose_drawing, LEFT, TOP)

            self.update_drawing()


    # -------------- animated rgb, each row with a different offset ------------------------
    def initialize_rgb_styles(self) -> list[int]:
        rgb_styles: list[int] = [self.toolbar.add_new_style('') for _ in
                                 range(ProfileReader.profile().console_penrose_size)]

        for i, style in enumerate(rgb_styles):
            self.toolbar.draw_style_canvas(LEFT, TOP + i, RIGHT, TOP + i + 1, style)

        return rgb_styles


    def update_rgb_styles(self, style_indexes: list[int]) -> None:
        for i, style in enumerate(style_indexes):
            self.toolbar.update_style(get_color_style(self.time_keeper.get_current_time() - pi * i / 10), style)


    # -------------- default look, no style animations ------------------------
    def initialize_mono_styles(self) -> list[int]:
        mono_style: int = self.toolbar.add_new_style('fg: #eeeeee')
        self.toolbar.draw_style_canvas(LEFT, TOP, RIGHT, BOTTOM, mono_style)
        return [mono_style]


    def update_mono_style(self, _style_indexes: list[int]) -> None:
        return


    # -------------- random colour for the whole triangle ------------------------
    def initialize_random_static_style(self) -> list[int]:
        mono_style: int = self.toolbar.add_new_style(
            f'fg: #{randint(0, 255):02x}{randint(0, 255):02x}{randint(0, 255):02x}'
        )
        self.toolbar.draw_style_canvas(LEFT, TOP, RIGHT, BOTTOM, mono_style)
        return [mono_style]


    def update_random_static_style(self, _style_indexes: list[int]) -> None:
        return
