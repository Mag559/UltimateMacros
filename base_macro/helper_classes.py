from time import time

class TerminationDetector:
    """
    Helper class that tracks events happening in quick succession

    Intended use for all macros is calling the should_terminate method whenever alt + ` is pressed
    This class will note down the time it happened
    If it happens x-1 more times during the window period should_terminate returns true,
    signaling the program should terminate
    """
    def __init__(self, event_count:int = 3, time_window:float = 1):
        """
        Initialize a TerminationDetector that tracks recent event timestamps to decide rapid succession termination.
        
        Parameters:
        	event_count (int): Number of recent events to track; determines the fixed size of the internal timestamp history.
        	time_window (float): Time window in seconds; if the oldest and newest tracked timestamps are within this span, termination is signaled.
        """
        self.event_count = event_count
        self.time_window = time_window
        self.event_times = [0.0] * event_count

    def should_terminate(self) -> bool:
        """
        Determine whether recent events occurred within the detector's configured time window.
        
        Updates the internal event timestamp history with the current time and checks whether the time difference between the newest and oldest recorded timestamps is less than the detector's time_window.
        
        Returns:
            True if the recorded events all occurred within the configured time window, False otherwise.
        """
        self.event_times.pop(0)
        self.event_times.append(time())
        if self.event_times[-1] - self.event_times[0] < self.time_window:
            return True
        return False