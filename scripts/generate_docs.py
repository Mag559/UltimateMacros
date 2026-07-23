from pathlib import Path
from um.repeater.instruction_declarations import create_parsers

parsers = create_parsers()

output = []
for name, parser in parsers.items():
    output.append(f"## {name}\n\n```\n{parser.format_help()}\n```\n")

Path("docs").mkdir(exist_ok=True)
docs_path = Path("docs/instructions.md")
docs_path.touch()
docs_path.write_text("\n".join(output))
