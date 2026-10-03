"""JSON loader for Killer and Thermo Sudoku instances."""

import json
from pathlib import Path
import random
from typing import Any

from sudoku import KillerCage, Sudoku


def _cell(value: Any) -> tuple[int, int]:
    if (not isinstance(value, list) or len(value) != 2
            or any(not isinstance(part, int) or isinstance(part, bool) for part in value)):
        raise ValueError(f"A cell must be a two-integer list [row, column], got {value!r}")
    return value[0], value[1]


def load_instance(path: str | Path, seed: int | None = None) -> Sudoku:
    """Load and initialize a Sudoku instance from a JSON file.

    Expected keys: ``grid`` (required), ``cages`` and ``thermos`` (optional).
    Grid zeros are empty cells. Coordinates are zero-based.
    """
    with Path(path).open("r", encoding="utf-8") as instance_file:
        data = json.load(instance_file)
    if not isinstance(data, dict):
        raise ValueError("Instance JSON must contain an object")
    if "grid" not in data:
        raise ValueError("Instance JSON is missing required 'grid'")

    raw_cages = data.get("cages", [])
    raw_thermos = data.get("thermos", [])
    if not isinstance(raw_cages, list) or not isinstance(raw_thermos, list):
        raise ValueError("'cages' and 'thermos' must be lists")

    cages = []
    for raw_cage in raw_cages:
        if not isinstance(raw_cage, dict) or "target" not in raw_cage or "cells" not in raw_cage:
            raise ValueError("Each cage must contain 'target' and 'cells'")
        target = raw_cage["target"]
        if not isinstance(target, int) or isinstance(target, bool):
            raise ValueError("Cage target must be an integer")
        if not isinstance(raw_cage["cells"], list) or not raw_cage["cells"]:
            raise ValueError("Cage cells must be a non-empty list")
        cages.append(KillerCage(target, tuple(_cell(cell) for cell in raw_cage["cells"])))

    thermos = []
    for raw_thermo in raw_thermos:
        if not isinstance(raw_thermo, list):
            raise ValueError("Each thermo must be a list of cells")
        thermos.append(tuple(_cell(cell) for cell in raw_thermo))

    return Sudoku.from_grid(data["grid"], cages, thermos, random.Random(seed))
