from time import time

from src.profiles import ProfileReader


class TerminationDetector:
    """
    Helper class that tracks events happening in quick succession

    Intended use:
    call the should_terminate method whenever SHORTCUT1 is pressed

    This class will note down the time it happened
    If it happens x-1 more times during the window period should_terminate returns true,
    signaling the program should terminate
    """
    def __init__(self,
                 event_count:int = ProfileReader.profile().macro_termination_event_count,
                 time_window:float = ProfileReader.profile().macro_termination_event_window
                 ):
        """
        Initialize a TerminationDetector that tracks recent event timestamps to decide rapid succession termination.
        
        Parameters:
        	event_count (int): how many events need to happen in the time window to result in termination
        	time_window (float): how wide should the time window be, in seconds
        """
        self.event_count = event_count
        self.time_window = time_window
        self.event_times = [0.0] * event_count

    def should_terminate(self) -> bool:
        """
        Registers an event happened at this time

        Returns:
            True if `event_count` such events happened in the time window and termination should take place
            False otherwise
        """
        self.event_times.pop(0)
        self.event_times.append(time())
        if self.event_times[-1] - self.event_times[0] < self.time_window:
            return True
        return False