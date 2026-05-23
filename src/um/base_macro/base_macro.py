from threading import Timer, Event
from logging import getLogger

from um.helper_classes import OrderedEmitter
from um.profiles import ProfileReader
from .macro_event_collector import MacroEventCollector, ImportantEvents
from um.base_macro.termination_detector import TerminationDetector


class BaseMacro:
    """
    Skeleton for a macro class.
    Utilizes a dependency injection for the event collector
    Sets a timer that closes the script after 5 min without any captured events
    """
    def __init__(self, collector:OrderedEmitter=None, timeout: float = ProfileReader.profile().macro_timeout):
        self.logger = getLogger(__name__)
        self._timeout = timeout
        if collector is None:
            collector = MacroEventCollector()
        self.event_collector: MacroEventCollector = collector

        self._terminator: TerminationDetector = TerminationDetector()
        self._exit_timer: Timer = Timer(self._timeout, self.stop)

        self._end_event: Event = Event()


    def start(self):
        self.logger.debug("Base Macro started")
        self._exit_timer.start()
        self.event_collector.add_caller(self._update)

        # block further execution until it's done
        self._end_event.wait()
        self.logger.debug("Base Macro finished running")


    def _update(self, event_code: ImportantEvents):
        """
        Reset the inactivity timeout and handle events that may trigger termination.
        
        Parameters:
            event_code (ImportantEvents): The event received from the event collector;
            certain event values (e.g., SHORTCUT1) may cause the macro to terminate if termination conditions are met.
        Returns:
            bool: True if the macro was terminated, False otherwise.
        Notes:
            This method resets the macro's inactivity timer and, for termination-related events,
            will invoke termination when appropriate.
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
        Stop the macro and cease input collection.
        """
        self.logger.debug("Shutting down base macro")
        self._exit_timer.cancel()
        self.event_collector.remove_caller(self._update)
        self._end_event.set()
