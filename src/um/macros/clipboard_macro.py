import pyperclip

from um.profiles import ProfileReader
import um.base_macro


class ClipboardMacro(um.base_macro.BaseMacro):
    """
    Ctrl + c or Ctrl + x -> override the next entry in the stack and make it current
    Ctrl + v -> paste the current clipboard contents, move the current entry to the previous and copy it to clipboard.
    3x Alt + ` in quick succession -> exit the program

    If the start / end of the list serving as the stack is reached, it loops
    """

    def __init__(self, init_size: int = ProfileReader.profile().macro_clipboard_stack_size):
        """
        :param init_size: Number of slots in the circular clipboard buffer,
        each slot is initialized to an empty string.
        """
        super().__init__()
        self.copy_entries: list[str] = [''] * init_size
        self.current_index: int = -1

    def _update(self, event_code: um.base_macro.ImportantEvent) -> bool:
        """
        Handle clipboard-related important events
        :param event_code: The clipboard event to handle (COPY, CUT, or PASTE are handled).
        :return: True if the macro was terminated, false otherwise
        """
        self.logger.debug(f"Entries before event processing: {self.copy_entries}")
        match event_code:
            case um.base_macro.ImportantEvent.COPY:
                self.store()
            case um.base_macro.ImportantEvent.CUT:
                self.store()
            case um.base_macro.ImportantEvent.PASTE:
                self.retrieve()
        self.logger.debug(f"Entries after event processing: {self.copy_entries}")

        return super()._update(event_code)

    def store(self) -> None:
        """
        Advance the circular buffer index and store the current system clipboard contents into that slot.
        """
        self.current_index = (self.current_index + 1) % len(self.copy_entries)
        self.copy_entries[self.current_index] = pyperclip.paste()

    def retrieve(self) -> None:
        """
        Advance the circular buffer to the previous entry and place that entry into the system clipboard.
        """
        self.current_index = (self.current_index - 1) % len(self.copy_entries)
        pyperclip.copy(self.copy_entries[self.current_index])
