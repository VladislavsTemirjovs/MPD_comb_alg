"""Run repeated Simulated Annealing trials on every categorized JSON instance."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
import statistics

from loader import load_instance
from simulated_annealing import AnnealingConfig, solve

ROOT = Path(__file__).resolve().parent
INSTANCE_DIR = ROOT / "instances"
DEFAULT_RESULTS_DIR = ROOT / "results"
INSTANCE_GROUPS = ("classic", "killer", "thermo", "killer_thermo")
RECORD_FIELDS = (
    "instance", "category", "run", "seed", "solved", "initial_score",
    "best_score", "optimal_score", "optimality_gap", "execution_time_seconds",
    "iterations", "restarts", "time_limit_seconds", "best_grid",
)
SUMMARY_FIELDS = (
    "instance", "category", "runs", "solved_runs", "success_rate",
    "average_best_score", "best_score", "average_time_seconds",
    "maximum_time_seconds", "average_iterations",
)


def discover_instances() -> list[tuple[str, Path]]:
    found = []
    for category in INSTANCE_GROUPS:
        folder = INSTANCE_DIR / category
        if folder.exists():
            found.extend((category, path) for path in sorted(folder.glob("*.json")))
    return found


def grid_as_string(grid) -> str:
    return "".join(str(value) for row in grid for value in row)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark the custom Simulated Annealing solver over categorized Sudoku instances."
    )
    parser.add_argument("--runs", type=int, default=5, help="Independent runs per puzzle (default: 5)")
    parser.add_argument("--time-limit", type=float, default=10.0,
                        help="Maximum seconds per run (default: 10; total worst case is puzzles × runs × limit)")
    parser.add_argument("--seed", type=int, default=42, help="Base seed for reproducible runs (default: 42)")
    parser.add_argument("--temperature", type=float, default=5.0, help="Initial SA temperature")
    parser.add_argument("--cooling-rate", type=float, default=0.9995, help="SA temperature multiplier")
    parser.add_argument("--output", type=Path, default=None,
                        help="CSV path for per-run records (default: timestamped file under results/)")
    args = parser.parse_args()

    if args.runs < 1:
        parser.error("--runs must be at least 1")
    if args.time_limit <= 0:
        parser.error("--time-limit must be greater than zero")

    instances = discover_instances()
    if not instances:
        parser.error("No JSON instances found under instances/{classic,killer,thermo,killer_thermo}/")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = args.output or (DEFAULT_RESULTS_DIR / f"benchmark_{stamp}.csv")
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path = output_path.with_name(f"{output_path.stem}_summary.csv")
    config = AnnealingConfig(args.temperature, args.cooling_rate, args.time_limit)
    grouped: dict[str, list[dict[str, object]]] = {}
    total = len(instances) * args.runs
    record_number = 0

    # Flush every run so completed measurements are retained if the benchmark is interrupted.
    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=RECORD_FIELDS)
        writer.writeheader()
        output_file.flush()
        for instance_index, (category, path) in enumerate(instances):
            for run_number in range(1, args.runs + 1):
                record_number += 1
                run_seed = args.seed + instance_index * 10_000 + run_number
                puzzle = load_instance(path, seed=run_seed)
                result = solve(puzzle, config, seed=run_seed)
                row = {
                    "instance": path.stem,
                    "category": category,
                    "run": run_number,
                    "seed": run_seed,
                    "solved": result.solved,
                    "initial_score": result.initial_score,
                    "best_score": result.best_score,
                    "optimal_score": 0,
                    "optimality_gap": result.best_score,
                    "execution_time_seconds": f"{result.execution_time:.6f}",
                    "iterations": result.iterations,
                    "restarts": result.restart_count,
                    "time_limit_seconds": args.time_limit,
                    "best_grid": grid_as_string(result.best.grid),
                }
                writer.writerow(row)
                output_file.flush()
                grouped.setdefault(path.stem, []).append(row)
                print(
                    f"[{record_number}/{total}] {path.stem} run {run_number}/{args.runs}: "
                    f"solved={result.solved}, score={result.best_score}, "
                    f"time={result.execution_time:.3f}s, iterations={result.iterations}"
                )

    with summary_path.open("w", newline="", encoding="utf-8") as summary_file:
        writer = csv.DictWriter(summary_file, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        for category, path in instances:
            rows = grouped[path.stem]
            times = [float(row["execution_time_seconds"]) for row in rows]
            scores = [int(row["best_score"]) for row in rows]
            iterations = [int(row["iterations"]) for row in rows]
            solved_runs = sum(bool(row["solved"]) for row in rows)
            writer.writerow({
                "instance": path.stem,
                "category": category,
                "runs": len(rows),
                "solved_runs": solved_runs,
                "success_rate": f"{solved_runs / len(rows):.2%}",
                "average_best_score": f"{statistics.mean(scores):.2f}",
                "best_score": min(scores),
                "average_time_seconds": f"{statistics.mean(times):.6f}",
                "maximum_time_seconds": f"{max(times):.6f}",
                "average_iterations": f"{statistics.mean(iterations):.1f}",
            })

    print(f"\nSaved {record_number} run records to {output_path}")
    print(f"Saved per-puzzle summary to {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
