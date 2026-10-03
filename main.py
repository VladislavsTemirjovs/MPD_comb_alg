"""Command-line entry point for inspecting a Sudoku instance."""

import argparse
from loader import load_instance
from simulated_annealing import AnnealingConfig, solve


def main() -> int:
    """Load an instance, build a starting candidate, and show its score."""
    parser = argparse.ArgumentParser(description="Solve Sudoku using Simulated Annealing")
    parser.add_argument("instance", help="Path to a Sudoku JSON instance")
    parser.add_argument("--seed", type=int, default=None, help="Seed for reproducible initialization")
    parser.add_argument("--temperature", type=float, default=5.0, help="Initial temperature")
    parser.add_argument("--cooling-rate", type=float, default=0.9995, help="Temperature multiplier per move")
    parser.add_argument("--time-limit", type=float, default=180.0,
                        help="Stop after this many seconds if no solution is found (default: 180)")
    args = parser.parse_args()

    try:
        sudoku = load_instance(args.instance, seed=args.seed)
        result = solve(sudoku, AnnealingConfig(args.temperature, args.cooling_rate,
                                               args.time_limit), seed=args.seed)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    print(f"Solved: {result.solved}")
    print(f"Initial score: {result.initial_score}")
    print(f"Best score: {result.best_score}")
    print(f"Iterations: {result.iterations}")
    print(f"Restarts: {result.restart_count}")
    print(f"Execution time: {result.execution_time:.6f} s")
    print("Best candidate:")
    for row in result.best.grid:
        print(" ".join(str(value) for value in row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
