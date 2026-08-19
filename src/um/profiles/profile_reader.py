import logging
from dataclasses import dataclass, field
import json
from pathlib import Path

from .directories_manager import COOKIES_PATH, PROFILES_PATH


class ProfileReader:
    """
    Singleton-ish manager of profiles.
    Stores the current profile in `profile_files/cookies.txt`,
    loads profiles with overrides stored in JSON files.
    Every profile must have a JSON file even if no overrides are desired,
    use an empty dictionary in that case.
    """
    _instance: ProfileReader = None

    @staticmethod
    def profile() -> Profile:
        """
        Get the current profile.
        :return: active, readonly profile
        """
        return ProfileReader._instance.profile

    @staticmethod
    def switch_profile(new_profile_name: str) -> None:
        """
        Hotswap the profile. Updates the grand majority (but not all) of the setting mid-running the program
        :param new_profile_name: which profile to switch to
        :return:
        """
        ProfileReader._instance._load_profile(new_profile_name)

    @staticmethod
    def reload_profile() -> None:
        """
        Reload the profile by rereading the overrides in the JSON file.
        Kinda useless unless you're changing the profile file while the program is running.
        :return:
        """
        ProfileReader._instance._load_profile(ProfileReader._instance.current_profile)

    def __init__(self):
        if ProfileReader._instance is not None:
            raise RuntimeError("ProfileReader is a singleton and has already been initialized")
        ProfileReader._instance = self
        self.current_profile: str
        self.profile: Profile

        if not COOKIES_PATH.is_file():
            self.current_profile = "default"
        else:
            with open(COOKIES_PATH, "r") as f:
                last_profile = f.readline().strip()
                if last_profile:
                    self.current_profile = last_profile
                else:
                    self.current_profile = "default"
        self._load_profile(self.current_profile)

    def _load_profile(self, profile_name: str) -> None:
        """
        Read the JSON profile file, create the Profile object, set the specified profile as current
        :param profile_name: what profile to load
        :return:
        """
        self.profile = Profile()
        self.current_profile = profile_name

        if not profile_name.endswith(".json"):
            profile_name += ".json"

        with open(PROFILES_PATH / profile_name, 'r') as f:
            self.profile.override_defaults(json.load(f))

        with open(COOKIES_PATH, 'w') as f:
            f.write(self.current_profile)


@dataclass
class Profile:
    """
    A collection of readonly profile settings.
    Defaults are defined below,
    all of them can be overridden in the associated JSON profile file.
    """
    _under_construction: bool = True

    def override_defaults(self, overrides: dict):
        """
        Override the default settings with the specified overrides.
        :param overrides: overrides in the form of a dictionary
        :return:
        """
        for name, attr in overrides.items():
            self.__setattr__(name, attr)
        _under_construction = False

    def __setattr__(self, name, value):
        if not self._under_construction:
            raise AttributeError("Modifying the profile is forbidden")

        if value is list:
            value = tuple(value)
        super().__setattr__(name, value)

    # ----------------- process related -----------------
    logging_level: int = logging.DEBUG

    # in bytes
    logging_min_size_to_clean: int = 20_000
    logging_uncleaned_size: int = 10_000

    # ----------------- console related -----------------
    console_timeout: float = 100

    console_detect_unfocus: bool = True

    console_toolbar_width: int = 125
    console_toolbar_height: int = 20

    console_prompt: str = "> "
    console_last_command_style: str = "fg:#ff0000"
    console_prompt_style: str = "bg:#0c0c0c fg:#cccccc"
    console_toolbar_style: str = "bg:#0c0c0c fg:#eeeeee noreverse"

    # um.console_prompt.console_drawer.ConsoleDrawerStyle
    console_penrose_style: int = 0

    console_penrose_spf: float = 0.05
    console_penrose_sleeping_spf: float = 0.5

    console_penrose_starting_angle: float = 0
    console_penrose_size: int = 20
    console_penrose_rotation_speed: float = 1.2

    pinned_directories: list[str] = field(default_factory=lambda: [str(Path.home())])

    # ----------------- macro related -----------------

    macro_event_collector_priority: int = 10
    macro_recorder_priority: int = -20

    macro_timeout: float = 300
    macro_termination_event_count: int = 3
    macro_termination_event_window: float = 1

    macro_clipboard_stack_size: int = 10

    macro_text_map_copy_delay: float = 0.1
    macro_text_map_paste_delay: float = 0.1

    macro_interpreter_mode: int = 0  # BaseInterpreter.Mode.END_ON_FAIL
    macro_interpreter_sleep_spf: float = 0.1

    macro_recorder_time_precision: int = 5

    # ----------------- receive and generate inputs -----------------

    input_double_click_time: float = 0.2
    # input_event_emission_delay: float = 0.15

    input_typing_wait_time: float = 0.03
    input_delay_before_enter: float = 0.5
    input_delay_between_tabs: float = 0.03

    input_clipboard_update_delay: float = 0.1

    # ----------------- matching images related -----------------
    match_monitor_number: int = 0

    match_taskbar_section: list[int] = (570, 1020, 1000, 60)
    match_whole_screen: list[int] = (0, 0, 1920, 1080)

    match_firefox_icon_confidence: float = 0.98
    match_wikamp_attendance_confidence: float = 0.9

    match_firefox_loading_wheel_delay: float = 0.3

    match_total_diff_allowed: float = 5.0
    match_individual_diff_allowed: int = 10
    match_mismatched_pixels_allowed: float = 0.1
    match_brightness_diff_allowed: float = 10.0

    match_wait_timeout: float = 10.0
    match_wait_check_interval: float = 0.2

    match_confidence: float = 0.8

    # ----------------- tool related -----------------
    screenshot_delay_before_save: float = 1.0
    screenshot_preview_spf: float = 0.1

    # ----------------- xyz related -----------------


# intensionally at import time
ProfileReader()
