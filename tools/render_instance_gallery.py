"""Render JSON Sudoku instances as PNG diagrams and assemble a Markdown gallery."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
INSTANCES = ROOT / "instances"
IMAGE_DIR = INSTANCES / "images"
GALLERY = INSTANCES / "PUZZLE_GALLERY.md"
SIZE = 540
MARGIN = 36
CELL = 52
GRID = CELL * 9
FONT_PATHS = (
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
)


def font(size):
    for path in FONT_PATHS:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def dashed_line(draw, start, end, fill, width=2, dash=5, gap=4):
    x1, y1 = start
    x2, y2 = end
    length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    if not length:
        return
    dx, dy = (x2 - x1) / length, (y2 - y1) / length
    pos = 0.0
    while pos < length:
        stop = min(pos + dash, length)
        draw.line((x1 + dx * pos, y1 + dy * pos, x1 + dx * stop, y1 + dy * stop), fill=fill, width=width)
        pos += dash + gap


def render(data, output, show_solution=False):
    image = Image.new("RGB", (SIZE, SIZE), "white")
    draw = ImageDraw.Draw(image)
    number_font = font(27)
    cage_font = font(11)
    x0 = y0 = MARGIN
    x1 = y1 = MARGIN + GRID

    # Thermometers are drawn underneath cage borders, clues, and grid lines.
    for thermo in data.get("thermos", []):
        points = [(x0 + c * CELL + CELL / 2, y0 + r * CELL + CELL / 2) for r, c in thermo]
        if len(points) > 1:
            draw.line(points, fill=(204, 215, 225), width=15, joint="curve")
            draw.line(points, fill=(112, 132, 151), width=2, joint="curve")
            bx, by = points[0]
            radius = 9
            draw.ellipse((bx - radius, by - radius, bx + radius, by + radius), fill=(204, 215, 225), outline=(112, 132, 151), width=2)

    # Dashed boundary of each cage (coordinates in the JSON are zero-based).
    for cage in data.get("cages", []):
        cells = {tuple(cell) for cell in cage["cells"]}
        top_left = min(cells)
        lr, lc = top_left
        draw.text((x0 + lc * CELL + 3, y0 + lr * CELL + 1), str(cage["target"]), fill=(35, 45, 55), font=cage_font)
        for r, c in cells:
            left, top = x0 + c * CELL, y0 + r * CELL
            right, bottom = left + CELL, top + CELL
            edges = [
                ((r - 1, c) not in cells, (left, top), (right, top)),
                ((r + 1, c) not in cells, (left, bottom), (right, bottom)),
                ((r, c - 1) not in cells, (left, top), (left, bottom)),
                ((r, c + 1) not in cells, (right, top), (right, bottom)),
            ]
            for visible, start, end in edges:
                if visible:
                    dashed_line(draw, start, end, (45, 65, 82), width=2, dash=5, gap=4)

    # Sudoku grid and bold 3x3 box lines.
    for index in range(10):
        pos = MARGIN + index * CELL
        width = 4 if index % 3 == 0 else 1
        color = (20, 25, 30) if index % 3 == 0 else (165, 172, 179)
        draw.line((MARGIN, pos, MARGIN + GRID, pos), fill=color, width=width)
        draw.line((pos, MARGIN, pos, MARGIN + GRID), fill=color, width=width)

    # Starting givens.
    displayed_grid = data["known_solution"] if show_solution else data["grid"]
    for r, row in enumerate(displayed_grid):
        for c, value in enumerate(row):
            if value:
                box = draw.textbbox((0, 0), str(value), font=number_font)
                tw, th = box[2] - box[0], box[3] - box[1]
                cx = x0 + c * CELL + CELL / 2
                cy = y0 + r * CELL + CELL / 2
                draw.text((cx - tw / 2, cy - th / 2 - 2), str(value), fill=(15, 20, 25), font=number_font)

    image.save(output)


def main():
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(path for folder in ("classic", "killer", "thermo", "killer_thermo")
                   for path in (INSTANCES / folder).glob("*.json"))
    sections = {
        "classic": "Classic Sudoku",
        "killer": "Killer Sudoku",
        "thermo": "Thermo Sudoku",
        "killer_thermo": "Killer + Thermo Sudoku",
    }
    lines = ["# Sudoku puzzle gallery", "",
             "Diagrams are rendered from the corresponding JSON files. They show the starting clues, cage sums, and thermometer paths.",
             "Variant fixtures are generated examples, not exact transcriptions of the linked source diagrams. Coordinates in JSON are zero-based.", ""]
    for folder in sections:
        group = [path for path in files if path.parent.name == folder]
        lines += [f"## {sections[folder]}", ""]
        for path in group:
            data = json.loads(path.read_text(encoding="utf-8"))
            image_name = f"{path.stem}.png"
            render(data, IMAGE_DIR / image_name)
            origin = data["source"].get("data_origin") if isinstance(data.get("source"), dict) else None
            details = origin or f"Dataset record: `{data['source']['record_id']}`"
            lines += [f"### {data['name']}", "", details, "",
                      f"![{data['name']} puzzle diagram](images/{image_name})", "",
                      f"JSON: [`{path.name}`]({path.relative_to(INSTANCES).as_posix()})", ""]
            refs = data.get("source", {}).get("rules_references", []) if isinstance(data.get("source"), dict) else []
            if refs:
                lines.insert(len(lines) - 1, "Sources: " + ", ".join(f"[rules reference]({url})" for url in refs))
                lines.insert(len(lines) - 1, "")
    GALLERY.write_text("\n".join(lines), encoding="utf-8")
    print(f"Rendered {len(files)} diagrams to {IMAGE_DIR} and wrote {GALLERY}.")


if __name__ == "__main__":
    main()
