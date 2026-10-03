"""Generate reproducible Killer/Thermo test fixtures from valid Sudoku grids."""

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "instances"
CLASSIC_SOURCE = "https://huggingface.co/datasets/prabinpanta0/Sudoku"
RULES = {
    "killer": "https://www.gmpuzzles.com/blog/2022/11/killer-thermo-sudoku-by-michael-rios/",
    "thermo": "https://www.gmpuzzles.com/blog/2015/02/thermo-sudoku-ashish-kumar/",
}

CLASSICS = [
    ("classic-000002", "600103709000940008405270136030062495004305801070081062007509000980600007350000904", "628153749713946258495278136831762495264395871579481362147529683982634517356817924"),
    ("classic-000009", "008060420490380516600900700100035274204106030573400801000200657052691040806053100", "318567429497382516625914783169835274284176935573429861931248657752691348846753192"),
    ("classic-000016", "712304058389006012005820009061087395008400001200605000900000524004060173027040980", "712394658389756412645821739461287395578439261293615847936178524854962173127543986"),
    ("classic-000026", "069000000803004010214760395001932048902000063708600901000200870300006000485170032", "569321487873594216214768395651932748942817563738645921196253874327486159485179632"),
    ("classic-000034", "029006103004000726506732490400020060062801574071005302650914207007500010003070040", "729486153834159726516732498485327961362891574971645382658914237247563819193278645"),
]


def as_grid(text):
    if len(text) != 81:
        raise ValueError(f"Expected 81 digits, got {len(text)}")
    return [[int(text[r * 9 + c]) for c in range(9)] for r in range(9)]


def valid_solution(grid):
    wanted = list(range(1, 10))
    return (
        all(sorted(row) == wanted for row in grid)
        and all(sorted(grid[r][c] for r in range(9)) == wanted for c in range(9))
        and all(sorted(grid[r + dr][c + dc] for dr in range(3) for dc in range(3)) == wanted
                for r in range(0, 9, 3) for c in range(0, 9, 3))
    )


def canonical(seed):
    rng = random.Random(seed)
    base = [[(r * 3 + r // 3 + c) % 9 + 1 for c in range(9)] for r in range(9)]
    digits = list(range(1, 10))
    rng.shuffle(digits)
    rows = []
    bands = list(range(3))
    rng.shuffle(bands)
    for band in bands:
        inner = list(range(3))
        rng.shuffle(inner)
        rows.extend(band * 3 + i for i in inner)
    cols = []
    stacks = list(range(3))
    rng.shuffle(stacks)
    for stack in stacks:
        inner = list(range(3))
        rng.shuffle(inner)
        cols.extend(stack * 3 + i for i in inner)
    return [[digits[base[r][c] - 1] for c in cols] for r in rows]


def make_clues(solution, seed, clue_count):
    rng = random.Random(seed)
    keep = set(rng.sample([(r, c) for r in range(9) for c in range(9)], clue_count))
    return [[solution[r][c] if (r, c) in keep else 0 for c in range(9)] for r in range(9)]


def make_cages(solution, seed):
    rng = random.Random(seed)
    cages = []
    for r in range(9):
        c = 0
        while c < 9:
            options = [size for size in (2, 3, 4) if size <= 9 - c]
            size = rng.choice(options) if options else 9 - c
            cells = [[r, k] for k in range(c, c + size)]
            cages.append({"target": sum(solution[r][k] for k in range(c, c + size)), "cells": cells})
            c += size
    return cages


def make_thermos(solution, seed, count=6):
    rng = random.Random(seed)
    board = [(r, c) for r in range(9) for c in range(9)]
    thermos = []
    for _ in range(count):
        starts = board[:]
        rng.shuffle(starts)
        path = None
        for start in starts:
            current = [start]
            while len(current) < 5:
                r, c = current[-1]
                options = [(nr, nc) for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
                           if 0 <= nr < 9 and 0 <= nc < 9 and (nr, nc) not in current
                           and solution[nr][nc] > solution[r][c]]
                if not options:
                    break
                current.append(rng.choice(options))
            if len(current) >= 3:
                path = current
                break
        if path is None:
            raise RuntimeError("Could not make a valid thermo path")
        thermos.append([[r, c] for r, c in path])
    return thermos


def save(relative_path, data):
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main():
    for number, (record, puzzle, answer) in enumerate(CLASSICS, 1):
        grid, solution = as_grid(puzzle), as_grid(answer)
        if not valid_solution(solution) or any(grid[r][c] and grid[r][c] != solution[r][c]
                                               for r in range(9) for c in range(9)):
            raise ValueError(f"Invalid source puzzle or answer: {record}")
        save(Path("classic") / f"classic_{number:02}.json", {
            "name": f"classic_{number:02}",
            "description": f"Published classic Sudoku sample {record}.",
            "source": {"dataset": CLASSIC_SOURCE, "record_id": record},
            "grid": grid, "cages": [], "thermos": [], "known_solution": solution,
        })

    for category, seed_offset, killer, thermo in (
        ("killer", 10, True, False), ("thermo", 20, False, True),
        ("killer_thermo", 30, True, True),
    ):
        for number in range(1, 6):
            seed = seed_offset + number
            solution = canonical(seed)
            data = {
                "name": f"{category}_{number:02}",
                "description": "Generated fixture from a valid completed grid; not an exact transcription of the linked published puzzle.",
                "source": {
                    "data_origin": "Generated for this project with the recorded seed.",
                    "rules_references": [RULES[k] for k, enabled in (("killer", killer), ("thermo", thermo)) if enabled],
                    "seed": seed,
                },
                "grid": make_clues(solution, seed, 30 if killer else 34),
                "cages": make_cages(solution, seed) if killer else [],
                "thermos": make_thermos(solution, seed) if thermo else [],
                "known_solution": solution,
            }
            save(Path(category) / f"{category}_{number:02}.json", data)
    print("Created 20 instance files under instances/{classic,killer,thermo,killer_thermo}.")


if __name__ == "__main__":
    main()
