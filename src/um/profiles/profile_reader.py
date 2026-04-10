import logging
from dataclasses import dataclass
from pathlib import Path
import json

PROFILES_PATH = Path(__file__).parents[3] / "profile_files"
COOKIES_PATH = PROFILES_PATH / "cookies.txt"


class ProfileReader:
    _instance: ProfileReader = None

    @staticmethod
    def profile() -> Profile:
        if ProfileReader._instance is None:
            ProfileReader._instance = ProfileReader()
        return ProfileReader._instance.profile


    @staticmethod
    def switch_profile(new_profile_name: str):
        ProfileReader._instance._load_profile(new_profile_name)


    @staticmethod
    def reload_profile():
        ProfileReader._instance._load_profile(ProfileReader._instance.current_profile)


    def __init__(self):
        self.current_profile: str
        self.profile: Profile

        with open(COOKIES_PATH, "r") as f:
            last_profile = f.readline().strip()
            if last_profile:
                self._load_profile(last_profile)
            else:
                self._load_profile("default")



    def _load_profile(self, profile_name: str):
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
    _under_construction: bool = True

    def override_defaults(self, overrides: dict):
        for name, attr in overrides.items():
            self.__setattr__(name, attr)
        _under_construction = False

    def __setattr__(self, name, value):
        if not self._under_construction:
            raise AttributeError("Modifying the profile is forbidden")

        if value is list:
            value = tuple(value)
        super().__setattr__(name, value)

    ################### process related ###################
    logging_level: int = logging.DEBUG

    ################### console related ###################
    console_timeout: float = 100

    console_detect_unfocus: bool = True

    console_toolbar_width: int = 125
    console_toolbar_height: int = 20

    console_prompt: str = "> "

    console_prompt_style: str = "bg:#0c0c0c fg:#cccccc"
    console_toolbar_style: str = "bg:#0c0c0c fg:#eeeeee noreverse"


    console_penrose_spf: float = 0.05
    console_penrose_sleeping_spf: float = 0.5

    console_penrose_starting_angle: float = 0
    console_penrose_size: int = 20
    console_penrose_rotation_speed: float = 1.2

    ################### macro related ###################

    macro_timeout: float = 300
    macro_termination_event_count: int = 3
    macro_termination_event_window: float = 1

    macro_clipboard_stack_size: int = 10

    macro_interpreter_mode: int = 0 # END_ON_FAIL, no easy way to serialize enum
    macro_interpreter_sleep_spf: float = 0.1

    macro_recorder_time_precision: int = 5
    macro_recorder_record_thread_delay: float = 0.1

    ################### receive and generate inputs ###################

    input_double_click_time: float = 0.2
    input_event_emission_delay: float = 0.15

    input_typing_wait_time: float = 0.03
    input_delay_before_enter: float = 0.5
    input_delay_between_tabs: float = 0.03

    ################### matching images related ###################
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


    ################### tool related ###################
    screenshot_delay_before_save: float = 1.0
    screenshot_preview_spf: float = 0.1


    ################### console related ###################
