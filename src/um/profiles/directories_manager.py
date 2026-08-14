from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = PROJECT_ROOT / "src"
TEST_ROOT = PROJECT_ROOT / "test"

PROFILES_PATH = PROJECT_ROOT / "profile_files"
COOKIES_PATH = PROFILES_PATH / "cookies.txt"

MACRO_FILES = PROJECT_ROOT / "macro_files"
REFERENCE_IMAGES = PROJECT_ROOT / "reference_images"

TEST_RESOURCES_DIR = TEST_ROOT / "resources"
