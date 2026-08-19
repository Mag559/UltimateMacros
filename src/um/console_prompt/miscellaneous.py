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
    def _view_dir(str_directory: str):
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

        _display(directory, 0, printer)
        console_base.toolbar.draw_on_canvas(printer.get_drawing(), 0, 0)

    def _display(directory: Path, indent: int, printer: NumpyPrinter):
        try:
            for item in directory.iterdir():
                if item.is_dir():
                    printer.print(f"{indent * ' '} {item.name}:")

                    _display(item, indent + 4, printer)
                    continue

                if not item.name.endswith(".txt"):
                    continue
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
