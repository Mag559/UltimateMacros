from logging import getLogger
from threading import Timer, Event

from um.helper_classes import OrderedEmitter
from um.profiles import ProfileReader
from .macro_event_collector import MacroEventCollector, ImportantEvent
from .status_window import StatusOverlay
from .termination_detector import TerminationDetector


class BaseMacro:
    """
    Base class for all macros.
    Handles listening to ImportantEvents,
    detecting the termination signal of 3x SHORTCUT1 and timeout when no events are received.
    """

    def __init__(
            self,
            collector: OrderedEmitter = None,
            timeout: float = ProfileReader.profile().macro_timeout,
            status_window: bool = ProfileReader.profile().macro_status_window,
            status_window_kwargs: dict | None = None
    ):
        """
        Initialize class and its dependencies.
        :param collector: object supplying the ImportantEvents,
        by default a MacroEventCollector hooked up to the InputCollector Singleton
        :param timeout: after how long without ImportantEvents should the macro terminate,
        default determined by ``macro_timeout`` in the profile
        :param status_window: spawn an overlay window to show macro status.
        :param status_window_kwargs: keyword arguments to pass to the overlay window
        """

        self.logger = getLogger(__name__)
        self._timeout = timeout

        if collector is None:
            self.event_collector: OrderedEmitter = MacroEventCollector()
        else:
            self.event_collector: OrderedEmitter = collector
        self.event_collector.add_callback(self._update)

        self._terminator: TerminationDetector = TerminationDetector()
        self._exit_timer: Timer = Timer(self._timeout, self.stop)

        self._end_event: Event = Event()
        self.status_window: StatusOverlay | None = None
        self.use_status_window = status_window
        if self.use_status_window:
            self.status_window = StatusOverlay(**(status_window_kwargs or {}))

    def start(self):
        """
        Start the base macro functionality and block further execution until termination.
        """
        self.logger.debug("Base Macro started")
        self._exit_timer.start()
        self.event_collector.run()
        if self.use_status_window:
            self.status_window.start()

        # block further execution until it's done
        self._end_event.wait()
        self.logger.debug("Base Macro finished running")

    def _update(self, event_code: ImportantEvent) -> bool:
        """
        Method intended to be overridden by derived classes for implementing most of their functionality.
        Resets the inactivity timer and checks for the termination signal.

        :param event_code: important event detected by the collector

        :return: True if the macro was terminated, false otherwise
        """
        self._exit_timer.cancel()
        self._exit_timer = Timer(self._timeout, self.stop)
        self._exit_timer.start()
        match event_code:
            case ImportantEvent.SHORTCUT1:
                self.logger.debug("Shortcut1")
                if self._terminator.should_terminate():
                    self.logger.info("Terminating due to repeated shortcut1")
                    self.stop()
                    return True
        return False

    def stop(self):
        """
        Stop the macro.
        """
        self.logger.debug("Shutting down base macro")
        self._exit_timer.cancel()
        self.event_collector.remove_callback(self._update)
        if self.use_status_window:
            self.status_window.stop()
        self._end_event.set()
