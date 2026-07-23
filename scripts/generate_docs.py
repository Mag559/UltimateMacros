import sys
from unittest.mock import MagicMock
from pathlib import Path

# Stub out heavy runtime deps not needed for building/printing parsers
for mod_name in (
    "pynput", "pynput.keyboard", "pynput.mouse",
    "prompt_toolkit",
    "numpy",
    "cv2",
    "PIL", "PIL.Image",
    "mss",
    "pyperclip",
    "action_completer"
):
    sys.modules[mod_name] = MagicMock()

from um.repeater.instruction_declarations import create_parsers

parsers = create_parsers()

output = []
for name, parser in parsers.items():
    output.append(f"## {name}\n\n```\n{parser.format_help()}\n```\n")

Path("docs").mkdir(exist_ok=True)
docs_path = Path("docs/instructions.md")
docs_path.touch()
docs_path.write_text("\n".join(output))
