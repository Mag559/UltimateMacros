import pyperclip

from src.profiles import ProfileReader
from src.base_macro import BaseMacro, ImportantEvents


class ClipboardMacro(BaseMacro):
    """
    Ctrl + c or Ctrl + x -> override the next entry in the stack, move the current entry to the next
    Ctrl + v -> paste the current entry, move the current entry to the previous
    3x Alt + ` in quick succession -> exit the program

    If the start / end of the list serving as the stack is reached, it loops
    """
    def __init__(self, init_size: int = ProfileReader.profile().macro_clipboard_stack_size):
        """
        Parameters:
            init_size (int): Number of slots in the circular clipboard buffer; each slot is initialized to an empty string.
        """
        super().__init__()
        self.copy_entries: list[str] = [''] * init_size
        self.current_index: int = -1


    def update(self, event_code: ImportantEvents):
        """
        Handle clipboard-related events by storing or retrieving entries based on the provided event code.
        
        Processes ImportantEvents.COPY and ImportantEvents.CUT by storing the current clipboard content,
        and processes ImportantEvents.PASTE by retrieving and applying the next clipboard entry.
        
        Parameters:
            event_code (ImportantEvents): The clipboard event to handle (COPY, CUT, or PASTE).
        """
        super().update(event_code)
        self.logger.debug(f"Entries before event processing: {self.copy_entries}")
        match event_code:
            case ImportantEvents.COPY:
                self.store()
            case ImportantEvents.CUT:
                self.store()
            case ImportantEvents.PASTE:
                self.retrieve()
        self.logger.debug(f"Entries after event processing: {self.copy_entries}")


    def store(self):
        """
        Advance the circular buffer index and store the current system clipboard contents into that slot.
        
        This overwrites the buffer entry at the new index with the clipboard text read from the system.
        The index wraps to the start when it reaches the buffer length.
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