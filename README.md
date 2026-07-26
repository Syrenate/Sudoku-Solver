# Sudoku Solver
This is my implementation of a sudoku puzzle solver, with preset puzzles and custom puzzle solving. Relies on pruning possible board states, and branching when pruning becomes redundant.

## Instructions
Clone the repository. Only the files `Puzzle.py`, `Solver.py` and `test_puzzles.csv` are necessary. `Test Solvers` are other iterations of `Puzzle.py` that are suboptimal or malfunctional.
- `Puzzle.py`: classes for the puzzle, its board, and a board tile.
- `Solver.py`: user interface methods. **Run this to interact with the solver.**
- `test_puzzles.csv`: some sample puzzles. Feel free to add more, using the following syntax:
  
      [puzzle name]|[row 1],[row 2],...,[row n]
  where each row is a string comprised of numbers (filled tiles) and either `0`, `.` or a space (empty tiles).

## TODO:
- Implement a GUI for puzzle creation and visualisation.
- Optimise board searching and reduce redundant searches.
