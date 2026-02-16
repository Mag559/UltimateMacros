import pyperclip

from base_macro import BaseMacro, ImportantEvents


class ClipboardMacro(BaseMacro):
    """
    Ctrl + c or Ctrl + x -> override the next entry in the stack, move the current entry to the next
    Ctrl + v -> paste the current entry, move the current entry to the previous
    3x Alt + ` in quick succession -> exit the program

    If the start / end of the list serving as the stack is reached, it loops
    """
    def __init__(self, init_size: int=10, debug_mode: bool = False):
        """
        Initialize the circular clipboard buffer and set up macro debug mode.
        
        Parameters:
            init_size (int): Number of slots in the circular clipboard buffer; each slot is initialized to an empty string.
            debug_mode (bool): If True, enables verbose debug output in the macro.
        """
        self.copy_entries: list[str] = [''] * init_size
        self.current_index: int = -1
        super().__init__(debug_mode=debug_mode)

    def update(self, event_code: ImportantEvents):
        """
        Handle clipboard-related events by storing or retrieving entries based on the provided event code.
        
        Processes ImportantEvents.COPY and ImportantEvents.CUT by storing the current clipboard content, and processes ImportantEvents.PASTE by retrieving and applying the next clipboard entry. Prints a brief debug message when debug_mode is enabled.
        
        Parameters:
            event_code (ImportantEvents): The clipboard event to handle (COPY, CUT, or PASTE).
        """
        super().update(event_code)
        if self.debug_mode:
            print(self.copy_entries)
        match event_code:
            case ImportantEvents.COPY:
                self.store()
                if self.debug_mode:
                    print("Copied")
                    print(f"Stored in index: {self.current_index}")
            case ImportantEvents.CUT:
                self.store()
                if self.debug_mode:
                    print("Cut")
                    print(f"Stored in index: {self.current_index}")
            case ImportantEvents.PASTE:
                self.retrieve()
                if self.debug_mode:
                    print("Pasted")
                    print(f"Retrieved from index: {self.current_index}")
        if self.debug_mode:
            print(self.copy_entries)


    def store(self):
        """
        Advance the circular buffer index and store the current system clipboard contents into that slot.
        
        This overwrites the buffer entry at the new index with the clipboard text read from the system. The index wraps to the start when it reaches the buffer length.
        """
        self.current_index = (self.current_index + 1) % len(self.copy_entries)
        self.copy_entries[self.current_index] = pyperclip.paste()

    def retrieve(self):
        """
        Advance the circular buffer to the previous entry and place that entry into the system clipboard.
        
        The method decrements the internal index with wrap-around and copies the entry at the new index to the system clipboard using pyperclip.
        """
        self.current_index = (self.current_index - 1) % len(self.copy_entries)
        pyperclip.copy(self.copy_entries[self.current_index])


if __name__ == "__main__":
    ClipboardMacro(100)