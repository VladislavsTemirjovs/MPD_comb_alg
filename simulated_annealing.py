"""A from-scratch Simulated Annealing solver for Sudoku candidates."""

from __future__ import annotations

from dataclasses import dataclass
import math
import random
import time

from evaluator import evaluate
from sudoku import Sudoku


@dataclass(frozen=True)
class AnnealingConfig:
    """Controls the temperature schedule and wall-clock run time."""

    initial_temperature: float = 5.0
    cooling_rate: float = 0.9995
    time_limit_seconds: float = 180.0

    def __post_init__(self) -> None:
        if self.initial_temperature <= 0:
            raise ValueError("initial_temperature must be greater than zero")
        if not 0 < self.cooling_rate < 1:
            raise ValueError("cooling_rate must be between zero and one")
        if self.time_limit_seconds <= 0:
            raise ValueError("time_limit_seconds must be greater than zero")


@dataclass
class AnnealingResult:
    """Best candidate and run statistics returned by the solver."""

    best: Sudoku
    initial_score: int
    best_score: int
    iterations: int
    restart_count: int
    execution_time: float

    @property
    def solved(self) -> bool:
        return self.best_score == 0


def _copy_candidate(source: Sudoku) -> Sudoku:
    candidate = Sudoku([row[:] for row in source.grid], source.cages, source.thermos)
    candidate.fixed = [row[:] for row in source.fixed]
    return candidate


def _fresh_start(template: Sudoku, rng: random.Random) -> Sudoku:
    clues = [[template.grid[r][c] if template.fixed[r][c] else 0 for c in range(9)]
             for r in range(9)]
    return Sudoku.from_grid(clues, template.cages, template.thermos, rng)


def solve(
    initial: Sudoku,
    config: AnnealingConfig | None = None,
    seed: int | None = None,
) -> AnnealingResult:
    """Run SA, accepting uphill moves with probability exp(-delta / temperature)."""
    settings = config or AnnealingConfig()
    rng = random.Random(seed)
    started = time.perf_counter()
    current = _copy_candidate(initial)
    current_score = evaluate(current)
    initial_score = current_score
    best = _copy_candidate(current)
    best_score = current_score
    iterations_done = 0
    restarts_done = 0

    deadline = started + settings.time_limit_seconds
    temperature = settings.initial_temperature
    while best_score > 0 and time.perf_counter() < deadline:
        if temperature < 1e-12:
            current = _fresh_start(initial, rng)
            current_score = evaluate(current)
            restarts_done += 1
            temperature = settings.initial_temperature
            continue

        candidate = _copy_candidate(current)
        if not candidate.random_box_swap(rng):
            break
        candidate_score = evaluate(candidate)
        delta = candidate_score - current_score
        if delta <= 0 or rng.random() < math.exp(-delta / temperature):
            current, current_score = candidate, candidate_score
        if candidate_score < best_score:
            best, best_score = candidate, candidate_score
        iterations_done += 1
        temperature *= settings.cooling_rate

    return AnnealingResult(best, initial_score, best_score, iterations_done,
                           restarts_done, time.perf_counter() - started)
