"""Render known solutions from all JSON instances as a Markdown gallery."""

import json
from pathlib import Path

from render_instance_gallery import render

ROOT = Path(__file__).resolve().parents[1]
INSTANCES = ROOT / "instances"
IMAGE_DIR = INSTANCES / "images" / "solutions"
GALLERY = INSTANCES / "PUZZLE_SOLUTIONS.md"
SECTIONS = {
    "classic": "Classic Sudoku",
    "killer": "Killer Sudoku",
    "thermo": "Thermo Sudoku",
    "killer_thermo": "Killer + Thermo Sudoku",
}


def main():
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Sudoku solution gallery",
        "",
        "Each board is rendered from the `known_solution` field in its JSON file. Variant constraint markings are retained for reference.",
        "",
    ]
    count = 0
    for folder, title in SECTIONS.items():
        files = sorted((INSTANCES / folder).glob("*.json"))
        lines += [f"## {title}", ""]
        for path in files:
            data = json.loads(path.read_text(encoding="utf-8"))
            if "known_solution" not in data:
                raise ValueError(f"Missing known_solution in {path}")
            image_name = f"{path.stem}_solution.png"
            render(data, IMAGE_DIR / image_name, show_solution=True)
            lines += [
                f"### {data['name']} solution",
                "",
                f"![{data['name']} solution diagram](images/solutions/{image_name})",
                "",
                f"Puzzle JSON: [`{path.name}`]({path.relative_to(INSTANCES).as_posix()})",
                "",
            ]
            count += 1
    GALLERY.write_text("\n".join(lines), encoding="utf-8")
    print(f"Rendered {count} solution diagrams to {IMAGE_DIR} and wrote {GALLERY}.")


if __name__ == "__main__":
    main()
