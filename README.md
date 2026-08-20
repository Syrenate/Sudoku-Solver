# Sudoku Solver
This is my implementation of a Sudoku puzzle solver, with preset puzzles and custom puzzle solving. Relies on pruning possible board states, and branching when pruning becomes redundant.

<p align="center">
  <img src="res/solver-gui-v1.png" alt="V1 of the GUI implementation for the solver"/>
</p>

## Instructions
Run `main.py` in the terminal, it will open a separate Qt window. Click to select a tile, enter a number to change the value, and press backspace to remove a value. Then press solve!

## TODO:
- Add an actual functioning GUI lol.
- Optimize board searching (i.e reduce redundant searches with human-derived algorithms).
