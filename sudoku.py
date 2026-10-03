"""Data model and block-preserving state operations for 9x9 Sudoku."""

from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Sequence

Cell = tuple[int, int]
Grid = list[list[int]]


@dataclass(frozen=True)
class KillerCage:
    """A Killer Sudoku cage and its required sum."""

    target: int
    cells: tuple[Cell, ...]


@dataclass
class Sudoku:
    """A Sudoku instance and one mutable candidate grid."""

    grid: Grid
    cages: tuple[KillerCage, ...] = ()
    thermos: tuple[tuple[Cell, ...], ...] = ()
    fixed: list[list[bool]] = field(init=False)

    def __post_init__(self) -> None:
        if len(self.grid) != 9 or any(len(row) != 9 for row in self.grid):
            raise ValueError("Sudoku grid must have exactly 9 rows and 9 columns")
        if any(not isinstance(value, int) or value not in range(10)
               for row in self.grid for value in row):
            raise ValueError("Grid values must be integers from 0 to 9")
        self.grid = [list(row) for row in self.grid]
        self.fixed = [[value != 0 for value in row] for row in self.grid]
        for cage in self.cages:
            for cell in cage.cells:
                self._validate_cell(cell)
        for thermo in self.thermos:
            if len(thermo) < 2:
                raise ValueError("Each thermometer must contain at least two cells")
            for cell in thermo:
                self._validate_cell(cell)

    @staticmethod
    def _validate_cell(cell: Cell) -> None:
        row, column = cell
        if not (0 <= row < 9 and 0 <= column < 9):
            raise ValueError(f"Cell coordinates must be between 0 and 8: {cell}")

    @classmethod
    def from_grid(
        cls,
        grid: Sequence[Sequence[int]],
        cages: Sequence[KillerCage] = (),
        thermos: Sequence[Sequence[Cell]] = (),
        rng: random.Random | None = None,
    ) -> "Sudoku":
        """Fill each box's missing digits randomly while preserving given clues."""
        generator = rng or random.Random()
        candidate = [list(row) for row in grid]
        if len(candidate) != 9 or any(len(row) != 9 for row in candidate):
            raise ValueError("Sudoku grid must have exactly 9 rows and 9 columns")
        if any(not isinstance(value, int) or value not in range(10)
               for row in candidate for value in row):
            raise ValueError("Grid values must be integers from 0 to 9")

        fixed = [[value != 0 for value in row] for row in candidate]
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                cells = [(r, c) for r in range(box_row, box_row + 3)
                         for c in range(box_col, box_col + 3)]
                present = [candidate[r][c] for r, c in cells if candidate[r][c] != 0]
                if len(present) != len(set(present)):
                    raise ValueError(f"Duplicate clues in 3x3 box at ({box_row}, {box_col})")
                missing = [value for value in range(1, 10) if value not in present]
                generator.shuffle(missing)
                empty = [(r, c) for r, c in cells if candidate[r][c] == 0]
                for (row, column), value in zip(empty, missing):
                    candidate[row][column] = value
        sudoku = cls(candidate, tuple(cages), tuple(tuple(t) for t in thermos))
        # Filled cells remain movable; only values provided in the input are clues.
        sudoku.fixed = fixed
        return sudoku

    def random_box_swap(self, rng: random.Random) -> bool:
        """Swap two non-clue values within one box; report whether a move occurred."""
        swappable_boxes: list[list[Cell]] = []
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                cells = [(r, c) for r in range(box_row, box_row + 3)
                         for c in range(box_col, box_col + 3) if not self.fixed[r][c]]
                if len(cells) >= 2:
                    swappable_boxes.append(cells)
        if not swappable_boxes:
            return False
        first, second = rng.sample(rng.choice(swappable_boxes), 2)
        r1, c1 = first
        r2, c2 = second
        self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]
        return True
