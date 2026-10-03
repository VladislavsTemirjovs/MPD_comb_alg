import random
import json
import tempfile
import unittest
from pathlib import Path

from evaluator import evaluate, row_penalty, column_penalty, killer_penalty, thermo_penalty
from sudoku import KillerCage, Sudoku
from loader import load_instance
from simulated_annealing import AnnealingConfig, solve


SOLUTION = [
    [1, 2, 3, 4, 5, 6, 7, 8, 9], [4, 5, 6, 7, 8, 9, 1, 2, 3],
    [7, 8, 9, 1, 2, 3, 4, 5, 6], [2, 3, 4, 5, 6, 7, 8, 9, 1],
    [5, 6, 7, 8, 9, 1, 2, 3, 4], [8, 9, 1, 2, 3, 4, 5, 6, 7],
    [3, 4, 5, 6, 7, 8, 9, 1, 2], [6, 7, 8, 9, 1, 2, 3, 4, 5],
    [9, 1, 2, 3, 4, 5, 6, 7, 8],
]


class SudokuFoundationTests(unittest.TestCase):
    def test_initialization_fills_each_box_and_preserves_clues(self):
        puzzle = [row[:] for row in SOLUTION]
        puzzle[0][0] = puzzle[1][1] = 0
        sudoku = Sudoku.from_grid(puzzle, rng=random.Random(42))
        self.assertEqual(sudoku.grid[0][1], SOLUTION[0][1])
        self.assertIn(sudoku.grid[0][0], range(1, 10))
        self.assertIn(sudoku.grid[1][1], range(1, 10))
        self.assertFalse(sudoku.fixed[0][0])
        self.assertFalse(sudoku.fixed[1][1])
        for br in (0, 3, 6):
            for bc in (0, 3, 6):
                box = [sudoku.grid[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)]
                self.assertEqual(set(box), set(range(1, 10)))

    def test_duplicate_box_clues_are_rejected(self):
        puzzle = [[0] * 9 for _ in range(9)]
        puzzle[0][0] = puzzle[1][1] = 2
        with self.assertRaises(ValueError):
            Sudoku.from_grid(puzzle, rng=random.Random(1))

    def test_swap_preserves_box_digits_and_fixed_cells(self):
        puzzle = [row[:] for row in SOLUTION]
        puzzle[0][0] = puzzle[0][1] = 0
        sudoku = Sudoku.from_grid(puzzle, rng=random.Random(7))
        fixed_values = {(r, c): sudoku.grid[r][c] for r in range(9) for c in range(9)
                        if sudoku.fixed[r][c]}
        self.assertTrue(sudoku.random_box_swap(random.Random(3)))
        for (r, c), value in fixed_values.items():
            self.assertEqual(sudoku.grid[r][c], value)
        box = [sudoku.grid[r][c] for r in range(3) for c in range(3)]
        self.assertEqual(set(box), set(range(1, 10)))

    def test_all_penalties_are_zero_for_valid_solution(self):
        cages = (KillerCage(3, ((0, 0), (0, 1))),)
        thermos = (((0, 0), (0, 1), (0, 2)),)
        sudoku = Sudoku([row[:] for row in SOLUTION], cages, thermos)
        self.assertEqual(row_penalty(sudoku), 0)
        self.assertEqual(column_penalty(sudoku), 0)
        self.assertEqual(killer_penalty(sudoku), 0)
        self.assertEqual(thermo_penalty(sudoku), 0)
        self.assertEqual(evaluate(sudoku), 0)

    def test_killer_and_thermo_violations_are_counted(self):
        sudoku = Sudoku([row[:] for row in SOLUTION],
                        (KillerCage(99, ((0, 0), (0, 1))),),
                        (((0, 2), (0, 1)),))
        self.assertGreater(killer_penalty(sudoku), 0)
        self.assertEqual(thermo_penalty(sudoku), 2)

    def test_json_loader_reads_cages_thermos_and_seed(self):
        data = {"grid": SOLUTION, "cages": [{"target": 3, "cells": [[0, 0], [0, 1]]}],
                "thermos": [[[0, 0], [0, 1]]]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "puzzle.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            loaded = load_instance(path, seed=42)
        self.assertEqual(len(loaded.cages), 1)
        self.assertEqual(len(loaded.thermos), 1)
        self.assertEqual(evaluate(loaded), 0)

    def test_solver_returns_zero_for_already_solved_instance(self):
        puzzle = [row[:] for row in SOLUTION]
        puzzle[0][0] = 0
        initial = Sudoku.from_grid(puzzle, rng=random.Random(4))
        result = solve(initial, AnnealingConfig(time_limit_seconds=0.2), seed=11)
        self.assertTrue(result.solved)
        self.assertEqual(result.best_score, 0)
        self.assertEqual(result.iterations, 0)
        self.assertTrue(result.best.fixed[0][1])
        self.assertFalse(result.best.fixed[0][0])

    def test_solver_preserves_clues_under_time_limit(self):
        puzzle = [row[:] for row in SOLUTION]
        puzzle[0][0] = puzzle[0][1] = puzzle[1][0] = puzzle[1][1] = 0
        initial = Sudoku.from_grid(puzzle, rng=random.Random(8))
        result = solve(initial, AnnealingConfig(time_limit_seconds=0.2), seed=7)
        for r in range(9):
            for c in range(9):
                if puzzle[r][c] != 0:
                    self.assertEqual(result.best.grid[r][c], puzzle[r][c])
        self.assertLessEqual(result.best_score, result.initial_score)
        self.assertLess(result.execution_time, 0.5)


if __name__ == "__main__":
    unittest.main()
