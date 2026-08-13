import asyncio
from time import time

from um.profiles import ProfileReader


class TimeKeeper:
    """
    Class responsible for keeping track of time,
    which pauses when the application is unfocused.
    """
    def __init__(self):
        self.focused = True

        self._time_backlog: float = 0.0
        self._paused_time: float = -1.0

    def on_unfocused(self) -> None:
        """
        Method called to signal the TimeKeeper that application is unfocused.
        Records the time this happened.
        :return:
        """
        self.focused = False
        self._paused_time = time()

    def on_focused(self) -> None:
        """
        Method called to signal the TimeKeeper that application is back in focus.
        Does not calculate the backlog and resume time itself,
        instead it's done when the spin task exits the `slow sleep loop` to smoothly continue its animation.
        :return:
        """
        self.focused = True

    async def drawing_sleep_if_unfocused(self) -> None:
        """
        Method handling the `slow sleep loop` logic for the triangle animation.
        Does nothing if in focus,
        sleeps while periodically checking the focus if unfocused,
        calculates the time application was unfocused, which is slightly inflated due to waiting for the periodic check.
        :return:
        """
        if self.focused or not ProfileReader.profile().console_detect_unfocus:
            return

        while not self.focused:
            await asyncio.sleep(ProfileReader.profile().console_penrose_sleeping_spf)

        # likely unnecessary guard
        if self._paused_time < 0:
            return

        self._time_backlog += time() - self._paused_time
        self._paused_time = -1

    def get_current_time(self) -> float:
        """
        Get the time elapsed by the TimeKeeper, adjusted for application being unfocused.
        Slightly inflated due to delaying the unpause logic,
        but guaranteed to be bigger or equal to every previous call result.
        Returns the moment application was unfocused, while unfocused.
        :return: time application has been unfocused for
        """
        if self._paused_time > 0:
            return self._paused_time - self._time_backlog
        return time() - self._time_backlog
