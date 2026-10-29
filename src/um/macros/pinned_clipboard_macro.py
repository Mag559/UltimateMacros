from time import sleep
import pyperclip

from um.profiles import ProfileReader
import um.base_macro


class PinnedClipboardMacro(um.base_macro.BaseMacro):
    """
    SHORTCUT1 -> copy pinned text into the clipboard or restore previous contents
    SHORTCUT2 -> cycle through pinned texts
    Ctrl + v -> (if pinned text selected) paste the current pinned text and restore previous clipboard contents
    3x Alt + ` in quick succession -> exit the macro

    Pinned texts are stored in the profile (to avoid this macro getting overly complicated to use)
    """

    def __init__(self, pinned_texts: list[str] = None):
        """
        :param pinned_texts: loaded from the current profile
        """
        super().__init__(status_window_kwargs={
            "name": "PinnedClipboardMacro",
            "state": "running",
            "details": f"Unpinned\nClipboard: {pyperclip.paste()}"
        })
        if pinned_texts is None:
            pinned_texts = ProfileReader.profile().macro_pinned_texts
        self.pinned_texts: list[str] = pinned_texts
        self.current_index: int = 0
        self._pinned: bool = False
        self._clipboard_buffer: str = ""

    def _update(self, event_code: um.base_macro.ImportantEvent) -> bool:
        """
        Handle clipboard-related important events
        :param event_code: The clipboard event to handle (SHORTCUT1, SHORTCUT2, or PASTE are handled).
        :return: True if the macro was terminated, false otherwise
        """
        match event_code:
            case um.base_macro.ImportantEvent.SHORTCUT1:
                if self._pinned:
                    pyperclip.copy(self._clipboard_buffer)
                    self._pinned = False
                else:
                    sleep(0.03)
                    self._clipboard_buffer = pyperclip.paste()
                    self._pinned = True
                    pyperclip.copy(self.pinned_texts[self.current_index])
            case um.base_macro.ImportantEvent.SHORTCUT2:
                self.current_index = (self.current_index + 1) % len(self.pinned_texts)
                if self._pinned:
                    pyperclip.copy(self.pinned_texts[self.current_index])
            case um.base_macro.ImportantEvent.PASTE:
                if self._pinned:
                    pyperclip.copy(self._clipboard_buffer)
                    self._pinned = False

        if self._pinned:
            self.status_window.set_details(
                f"Index: {self.current_index}\nClipboard: {pyperclip.paste()}"
            )
        else:
            self.status_window.set_details(
                f"Unpinned\nClipboard: {pyperclip.paste()}"
            )

        return super()._update(event_code)

