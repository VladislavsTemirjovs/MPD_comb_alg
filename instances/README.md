# Sudoku test instances

The benchmark set includes 20 Sudoku instances in four groups, with five puzzles in each group:

- `classic/` - classic Sudoku
- `killer/` - Killer Sudoku
- `thermo/` - Thermo Sudoku
- `killer_thermo/` - Sudoku with both Killer and Thermo constraints

The separate `hard/` folder contains three Killer Sudoku puzzles with cage clues but no initial cell values. They are provided as additional solver examples and are not part of the 20-instance benchmark set.

Each JSON file contains a puzzle grid and its variant constraints. Benchmark instances also include a `known_solution` field for reference validation; the solver does not use it. The `hard/` puzzles have no initial cell values and do not include a reference solution. Cage and thermometer coordinates use zero-based `[row, column]` notation.

## Sources

The classic Sudoku puzzles and their answer grids are from the [Hugging Face Sudoku dataset](https://huggingface.co/datasets/prabinpanta0/Sudoku), released under the MIT license. Each classic puzzle records its dataset record ID in its JSON file.

The Killer and Thermo JSON files include links to references for the corresponding puzzle rules. These links are provided as rule references; the JSON files define the particular test instances used by this project.

## Run an instance

From the project root, run a puzzle with:

```powershell
python main.py instances/classic/classic_01.json --seed 1
python main.py instances/killer/killer_01.json --seed 1
python main.py instances/thermo/thermo_01.json --seed 1
python main.py instances/killer_thermo/killer_thermo_01.json --seed 1
python main.py instances/hard/hard_1.json --seed 1
```

The `--seed` option makes a run reproducible. To run five trials for each instance and save per-run records and summaries as CSV files, use:

```powershell
python benchmark.py --runs 5 --time-limit 30 --seed 42
```

Puzzle diagrams are collected in [`PUZZLE_GALLERY.md`](PUZZLE_GALLERY.md), and reference solution diagrams are in [`PUZZLE_SOLUTIONS.md`](PUZZLE_SOLUTIONS.md).
