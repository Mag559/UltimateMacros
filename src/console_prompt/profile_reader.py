from dataclasses import dataclass
from pathlib import Path
import json

PROFILES = Path(__file__).parents[2] / "profiles"
COOKIES = PROFILES / "cookies.txt"


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


    def __init__(self):
        self.current_profile: str
        self.profile: Profile

        with open(COOKIES, "r") as f:
            last_profile = f.readline().strip()
            if last_profile:
                self._load_profile(last_profile)
            else:
                self._load_profile("default")



    def _load_profile(self, profile_name: str):
        self.profile = Profile()
        
        with open(PROFILES / (profile_name + ".json"), 'r') as f:
            self.profile.override_defaults(json.load(f))

        self.current_profile = profile_name

        with open(COOKIES, 'w') as f:
            f.write(self.current_profile)



@dataclass
class Profile:
    _under_construction: bool = True
    a: str = '1'
    b: int = 1
    c: float = 1.0

    def override_defaults(self, overrides: dict):
        for name, attr in overrides.items():
            self.__setattr__(name, attr)
        _under_construction = False

    def __setattr__(self, name, value):
        if not self._under_construction:
            return
        super().__setattr__(name, value)