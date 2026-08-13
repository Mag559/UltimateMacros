from threading import Timer, Event
from logging import getLogger

from um.helper_classes import OrderedEmitter
from um.profiles import ProfileReader
from .macro_event_collector import MacroEventCollector, ImportantEvents
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
            timeout: float = ProfileReader.profile().macro_timeout
    ):
        """
        Initialize class and its dependencies.
        :param collector: object supplying the ImportantEvents,
        by default a MacroEventCollector hooked up to the InputCollector Singleton
        :param timeout: after how long without ImportantEvents should the macro terminate,
        default determined by ``macro_timeout`` in the profile
        """
        self.logger = getLogger(__name__)
        self._timeout = timeout
        if collector is None:
            self.event_collector: OrderedEmitter = MacroEventCollector()
        else:
            self.event_collector: OrderedEmitter = collector

        self._terminator: TerminationDetector = TerminationDetector()
        self._exit_timer: Timer = Timer(self._timeout, self.stop)

        self._end_event: Event = Event()

    def start(self):
        """
        Start the base macro functionality and block further execution until termination.
        """
        self.logger.debug("Base Macro started")
        self._exit_timer.start()
        self.event_collector.add_caller(self._update)

        # block further execution until it's done
        self._end_event.wait()
        self.logger.debug("Base Macro finished running")

    def _run(self):
        """
        Non-blocking version of start, intended for derived classes,
        which have no need to artificially block the main thread
        """
        self.logger.debug("Base Macro started asynchronously")
        self._exit_timer.start()
        self.event_collector.add_caller(self._update)

    def _update(self, event_code: ImportantEvents) -> bool:
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
            case ImportantEvents.SHORTCUT1:
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
        self.event_collector.remove_caller(self._update)
        self._end_event.set()
