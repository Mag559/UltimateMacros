import logging
from threading import Thread
from collections.abc import Callable


class LoggingThread(Thread):
    def __init__(self, name: str, target: Callable, group=None,
                 args=(), kwargs=None, *, daemon=None, context=None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon, context=context)
        self.logger = logging.getLogger(name)
        self.logger.debug(f"Thread initialized")

    def run(self):
        try:
            self.logger.debug(f"Thread running")
            super().run()
        except BaseException as e:
            self.logger.exception(f"{e}")
            raise
