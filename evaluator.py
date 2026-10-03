"""Objective function for classic, Killer, and Thermo Sudoku constraints."""

from sudoku import Sudoku


def duplicate_penalty(values: list[int]) -> int:
    """Count repeated entries beyond the first occurrence."""
    return len(values) - len(set(values))


def row_penalty(sudoku: Sudoku) -> int:
    return sum(duplicate_penalty(row) for row in sudoku.grid)


def column_penalty(sudoku: Sudoku) -> int:
    return sum(duplicate_penalty([sudoku.grid[r][c] for r in range(9)]) for c in range(9))


def killer_penalty(sudoku: Sudoku) -> int:
    penalty = 0
    for cage in sudoku.cages:
        values = [sudoku.grid[row][column] for row, column in cage.cells]
        penalty += abs(sum(values) - cage.target) + duplicate_penalty(values)
    return penalty


def thermo_penalty(sudoku: Sudoku) -> int:
    penalty = 0
    for thermo in sudoku.thermos:
        values = [sudoku.grid[row][column] for row, column in thermo]
        penalty += sum(max(0, left - right + 1) for left, right in zip(values, values[1:]))
    return penalty


def evaluate(sudoku: Sudoku) -> int:
    """Return total constraint violation; zero denotes a valid solution."""
    return (row_penalty(sudoku) + column_penalty(sudoku)
            + killer_penalty(sudoku) + thermo_penalty(sudoku))
