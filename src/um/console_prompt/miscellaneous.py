from collections.abc import Generator
from pathlib import Path

from um.profiles import PROFILES_PATH, ProfileReader
from .console_base import ConsoleBase
from .numpy_printer import NumpyPrinter
from .path_completer import UmPathCompleter

RESTART_CODE = 10


def setup_misc(console_base: ConsoleBase) -> None:
    """
    Registers miscellaneous actions like exiting, restarting, switching profiles etc.
    :param console_base: a bridge to some of the console Main's functionality
    :return:
    """
    completer = console_base.completer

    @completer.action("exit")
    @completer.action("quit")
    @completer.action("q")
    def _exit():
        raise SystemExit()

    @console_base.default
    def _view() -> None:
        print("Recursively list subdirectories and files in the given directory.")

    @completer.action("view")
    @completer.param(
        UmPathCompleter(
            True,
            get_paths=lambda: ProfileReader.profile().pinned_directories,
        ),
        cast=str
    )
    @completer.param(
        ["-1", "0", "1"],
        cast=int,
        display_meta=lambda _, param:
        {
            "-1": "infinite depth",
            "0": "only direct contents",
            "1": "up to subdirectory content"
        }[param]
    )
    @completer.param(
        [".txt", ".json", ".ins", ".py"],
        cast=str,
    )
    def _view_dir(str_directory: str, depth: int = -1, extension: str = ""):
        pinned_directories: list[Path] = [Path(directory) for directory in ProfileReader.profile().pinned_directories]

        printer: NumpyPrinter = NumpyPrinter()
        directory: Path = Path(str_directory)
        for pinned_dir in pinned_directories:
            if (
                    directory.name == pinned_dir.name or
                    (len(directory.parents) >= 2 and directory.parents[-2].name == pinned_dir.name)
            ):
                directory = pinned_dir.parent.joinpath(directory)
                break
        else:
            if not directory.is_absolute():
                print("Directory not found.")
                return

        gen: Generator = _display(directory, printer, depth, extension)
        for _ in gen:
            pass
        console_base.toolbar.draw_on_canvas(printer.get_drawing(), 0, 0)

    def _display(
            directory: Path,
            printer: NumpyPrinter,
            depth: int,
            extension: str,
            indent: int = 0,
    ) -> Generator[bool, None, None]:
        """
        Recursively display directory contents.
        Directories with no files of matching extension (and no subdirectories with such files) are not displayed.
        Directories and files beginning with "." are not displayed.
        :param directory: the starting directory
        :param printer: NumpyPrinter object used to convert lines of text into sth displayable on the bottom toolbar.
        :param depth: how many layers deep should the display be (negative means infinite, 0 means only direct contents)
        :param extension: what extension should the displayed files have, due to implementation via
        `str.endswith`, not entirely limited to just extensions. empty string accepts all files
        :param indent: number of spaces to display before file/dir name (the larger, the deeper)
        :return: bool Generator whether the parent directory should be displayed
        (not straight up bool to keep the correct order of printing: directory -> subdirectory -> file)
        """
        try:
            for item in directory.iterdir():
                if not printer.has_room():
                    return
                if item.name.startswith("."):
                    continue
                if item.is_dir():
                    # if out of depth, display the dir
                    if depth == 0:
                        yield True
                        printer.print(f"{indent * ' '} {item.name}/")
                        continue

                    non_empty: bool = False
                    for is_content in _display(item, printer, depth - 1, extension, indent + 4):
                        # guard in case of False yields
                        if not is_content:
                            continue

                        # only the first info that it is non-empty is important
                        if not non_empty:
                            # first signal higher up
                            yield True
                            # then print yourself
                            printer.print(f"{indent * ' '} {item.name}/")
                            non_empty = True

                    continue

                if not item.name.endswith(extension):
                    continue

                yield True
                printer.print(f"{indent * ' '} {item.name}")

        except OSError:
            printer.print(f"{indent * ' '} X directory inaccessible.")

    # @completer.action("notepad")
    # @completer.param(
    #     PathCompleter(
    #         False,
    #         lambda: ProfileReader.profile().pinned_directories,
    #         lambda path: path.endswith('.txt') or (path.find(".") == -1)
    #     ),
    #     cast=str
    # )
    # def _notepad(file_name: str):
    #     console_base.focus_release()
    #     if not file_name.endswith('.txt'):
    #         file_name += '.txt'
    #     path_to_open = Path(CURRENT_SEMESTER_DIR / file_name)
    #     if not path_to_open.exists() or path_to_open.is_dir():
    #         return
    #
    #     os.startfile(path_to_open)

    @completer.action("profile")
    @completer.param(
        [item.name.rstrip(".json") for item in PROFILES_PATH.iterdir() if item.name.endswith(".json")],
        cast=str
    )
    def _profile(profile: str = ""):
        if profile == "":
            ProfileReader.reload_profile()
        else:
            ProfileReader.switch_profile(profile)

    @completer.action("restart")
    def _restart():
        raise SystemExit(RESTART_CODE)
