import os
from collections.abc import Callable, Iterable

from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document


class UmPathCompleter(Completer):
    """
    PathCompleter class from `prompt_toolkit.completion`
    modified to easier implement distinguishing directories by starting the path from a pinned directory.
    Complete for Path variables.

    :param get_paths: Callable which returns a list of directories to look into
                      when the user enters a relative path.
    :param file_filter: Callable which takes a filename and returns whether
                        this file should show up in the completion. ``None``
                        when no filtering has to be done.
    :param min_input_len: Don't do autocompletion when the input string is shorter.
    :param expanduser: should `~` be expanded to the users (home / Users) directory
    """

    def __init__(
        self,
        only_directories: bool = False,
        get_paths: Callable[[], list[str]] | None = None,
        file_filter: Callable[[str], bool] | None = None,
        min_input_len: int = 0,
        expanduser: bool = False,
    ) -> None:
        self.only_directories = only_directories
        self.get_paths = get_paths or (lambda: [""])
        self.file_filter = file_filter or (lambda _: True)
        self.min_input_len = min_input_len
        self.expanduser = expanduser

    @staticmethod
    def _find_files_with_prefix(parent_dir: str, prefix: str) -> list[tuple[str, str]]:
        possibilities: list[tuple[str, str]] = []
        for possible_path in os.listdir(parent_dir):
            if os.path.basename(possible_path).startswith(prefix):
                possibilities.append((parent_dir, possible_path))
        return possibilities

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        text = document.text_before_cursor

        # Complete only when we have at least the minimal input length,
        # otherwise, we can too many results and autocompletion will become too
        # heavy.
        if len(text) < self.min_input_len:
            return

        try:
            # Do tilde expansion.
            if self.expanduser:
                text = os.path.expanduser(text)

            file_name: str = os.path.basename(text)

            # directory name, file name
            possibilities: list[tuple[str, str]] = []

            if os.path.isabs(text):
                # absolute path, don't try to match it to a pinned dir
                parent_dir: str = os.path.dirname(text)
                possibilities = self._find_files_with_prefix(parent_dir, file_name)

                print("abs")

            elif os.path.dirname(text) == "":  # pathlib has parents, but decides the parent of `name/` isn't `name`
                # only the name of the pinned directory
                for pinned_dir in self.get_paths():
                    if os.path.basename(pinned_dir).startswith(file_name):
                        possibilities.append(
                            (os.path.dirname(pinned_dir), os.path.basename(pinned_dir))
                        )

                print("pinned")
            else:
                i: str = os.path.dirname(text)
                pinned_dir_name: str = i
                while i != "":
                    pinned_dir_name = i
                    i = os.path.dirname(i)
                    if i == pinned_dir_name:
                        return

                print(f"normal in {pinned_dir_name}")
                for directory in self.get_paths():
                    if os.path.basename(directory) == pinned_dir_name:
                        pinned_directory: str = directory
                        break
                else:
                    return

                full_path: str = os.path.join(os.path.dirname(pinned_directory), text)

                print(f"fullpath: {full_path}")

                possibilities = self._find_files_with_prefix(os.path.dirname(full_path), file_name)

            # Sort
            possibilities = sorted(possibilities, key=lambda p: p[1])

            print(f"Possibilities: {possibilities}")

            # Yield them.
            for dir_name, possible_name in possibilities:
                full_path = os.path.join(dir_name, possible_name)

                if not self.file_filter(full_path):
                    continue

                completion = possible_name[len(file_name):]

                if os.path.isdir(full_path):
                    # For directories, add a slash to the filename.
                    # (We don't add them to the `completion`. Users can type it
                    # to trigger the autocompletion themselves.)
                    possible_name += "/"
                elif self.only_directories:
                    continue

                yield Completion(
                    text=completion,
                    start_position=0,
                    display=possible_name,
                )
        except OSError:
            pass
