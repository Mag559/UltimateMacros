from threading import Timer
from logging import getLogger

from .input_collector import InputCollector, ImportantEvents
from .helper_classes import TerminationDetector
from .signal_interfaces import Observer


class BaseMacro(Observer[ImportantEvents]):
    """
    Skeleton for a macro class.
    Utilizes a dependency injection for the input collector
    Sets a timer that closes the script after 5 min without any captured events

    Automatically starts at the end of the constructor
    """
    def __init__(self, collector:InputCollector=None, timeout: float = 300, debug_mode: bool = False):
        """
        Initialize the BaseMacro, subscribe to the input collector, start the inactivity timer, and begin collecting inputs.
        
        Parameters:
            collector (InputCollector): Input source to observe for events; subscribed to receive updates. Default is a new InputCollector instance.
            timeout (float): Number of seconds of inactivity before the macro automatically terminates.
            debug_mode (bool): If True, enable debug output during termination.
        """
        self.logger = getLogger(__name__)
        self.timeout = timeout
        if collector is None:
            collector = InputCollector(debug_mode=debug_mode)
        self.input_collector: InputCollector = collector
        self.debug_mode = debug_mode

        self.subscribe(self.input_collector)
        self.terminator: TerminationDetector = TerminationDetector()
        self.exit_timer: Timer = Timer(self.timeout, self.terminate)
        self.exit_timer.start()

        # start collecting inputs
        self.input_collector.start()

        # wait for it to finish before ending constructor
        self.input_collector.join()

        self.logger.debug("Base Macro constructor completed")

    def update(self, event_code: ImportantEvents):
        """
        Reset the inactivity timeout and handle events that may trigger termination.
        
        Parameters:
            event_code (ImportantEvents): The event received from the input collector; certain event values (e.g., SHORTCUT1) may cause the macro to terminate if termination conditions are met.
        Returns:
            bool: True if the macro was terminated, False otherwise.
        Notes:
            This method resets the macro's inactivity timer and, for termination-related events, will invoke termination when appropriate.
        """
        self.exit_timer.cancel()
        self.exit_timer = Timer(self.timeout, self.terminate)
        self.exit_timer.start()
        match event_code:
            case ImportantEvents.SHORTCUT1:
                if self.terminator.should_terminate():
                    self.terminate()
                    return True
        return False


    def terminate(self):
        """
        Stop the macro and cease input collection.
        
        If debug_mode is True, prints "Shutting down". Stops the input collector's listener so no further input events are received.
        """
        self.logger.debug("Shutting down base macro")
        if self.debug_mode:
            print("Shutting down")
        self.input_collector.stop()


if __name__ == "__main__":
    BaseMacro(debug_mode=True)