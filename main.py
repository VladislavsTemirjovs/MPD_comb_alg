"""Command-line entry point for inspecting a Sudoku instance."""

import argparse
import time

from evaluator import evaluate
from loader import load_instance


def main() -> int:
    """Load an instance, build a starting candidate, and show its score."""
    parser = argparse.ArgumentParser(description="Load and evaluate a Sudoku candidate")
    parser.add_argument("instance", help="Path to a Sudoku JSON instance")
    parser.add_argument("--seed", type=int, default=None, help="Seed for reproducible initialization")
    args = parser.parse_args()

    started = time.perf_counter()
    try:
        sudoku = load_instance(args.instance, seed=args.seed)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    elapsed = time.perf_counter() - started

    print(f"Initial score: {evaluate(sudoku)}")
    print(f"Initialization time: {elapsed:.6f} s")
    print("Starting candidate:")
    for row in sudoku.grid:
        print(" ".join(str(value) for value in row))
    print("Note: the Simulated Annealing solver is not implemented yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
