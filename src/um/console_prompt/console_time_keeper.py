import asyncio
from collections.abc import Callable
from time import time

from um.profiles import ProfileReader


class TimeKeeper:
    def __init__(self, on_exit_timer_timeout: Callable[[], None]):
        self.focused = True

        self._time_backlog: float = 0.0
        self._paused_time: float = -1.0

        self._on_exit_timer_timeout = on_exit_timer_timeout

    def on_unfocused(self):
        self.focused = False
        self._paused_time = time()

    def on_focused(self):
        self.focused = True
        # accounting for the paused time is further deferred to when the spin task exits slow sleep loop

    async def drawing_sleep_if_unfocused(self):
        if self.focused or not ProfileReader.profile().console_detect_unfocus:
            return

        while not self.focused:
            await asyncio.sleep(ProfileReader.profile().console_penrose_sleeping_spf)

        if self._paused_time < 0:
            return

        self._time_backlog += time() - self._paused_time

    def get_current_time(self) -> float:
        return time() - self._time_backlog
