import time
import copy

# Main problem with V1 was the absurd lack of attention to readability and a coherent structure. 
# So when branching didnt work, it was a clusterfuck to debug. At least for me. Won't make that mistake again.

class Tile:
    """A tile is a value specifying its board position, storing possible states in its board. Pos should be (i,j), where i is horizontal position and j is vertical (read from top left to bottom right)."""
    def __init__(self, value, pos):
        """"value: character found in configuation. pos: position in the puzzle board."""
        if value in ['.', '0', ' ']:
            self.value = 0
            self.states = list(range(1, 10))
        else:
            self.value = int(value)
            self.states = [self.value]
        self.position = pos

    def __str__(self): 
        return str(self.value) if self.is_filled() else '.'

    def is_filled(self) -> bool: 
        """Identifies if the tile is filled."""
        return self.value != 0


class Puzzle:
    """A puzzle stores a given board configuration by a matrix of Tiles, containing methods to find a solution and extract data from the board."""
    def __init__(self, config: list[str]):
        """Initialise a puzzle board based on a config (list of rows of the puzzle)."""
        self.board = []
        for j, line in enumerate(config):
            tile_line = [Tile(value, (i, j)) for i, value in enumerate(line)]
            self.board.append(tile_line)

        self.is_solved = False
        self.is_solvable = True
        self.state_changed = False

    def __str__(self): 
        output = ""
        for j in range(9):
            line = ""
            for i in range(9):
                value = str(self.get_tile((i, j)))
                line += (value if value != '0' else '.') + (" | " if (i+1) % 3 == 0 and i != 8 else " ")
            output += line + ('\n' if j != 8 else '') + (('-' * 21) + '\n' if (j+1) % 3 == 0 and j != 8 else '')
        return output 


    def fill_tile(self, value: int, pos: tuple[int]):
        """Replace a tile at a specified position with a specified value."""
        self.board[pos[1]][pos[0]] = Tile(value, pos)

    def get_tile(self, pos: tuple[int]) -> Tile:
        """Returns the tile at a given position"""
        return self.board[pos[1]][pos[0]]
    
    def get_rows(self) -> list[list[Tile]]:
        """Returns the rows of the board."""
        return self.board
    
    def get_columns(self) -> list[list[Tile]]:
        """Returns the columns of the board."""
        columns = []
        for i in range(9):
            columns.append([self.get_tile((i, j)) for j in range(9)])
        return columns
    
    def get_squares(self) -> list[list[Tile]]:
        """Returns all squares on the board (each 3x3 cell of tiles)."""
        squares = []
        # Loop through the top-left corner of each square.
        for i0 in [0,3,6]:
            for j0 in [0,3,6]:
                square = []

                # Loop through each tile in the current square.
                for i in range(i0, i0+3):
                    for j in range(j0, j0+3):
                        square.append(self.get_tile((i, j)))
                squares.append(square)

        return squares
    
    def get_tiles(self, condition = (lambda x: x)) -> list[Tile]:
        """Returns all tiles in the board with a specified condition on each tile."""
        tiles = []
        for i in range(9):
            for j in range(9):
                tile = self.get_tile((i, j))
                if condition(tile):
                    tiles.append(tile)
        return tiles


    def valid_tiles(self, tiles: list[Tile]) -> bool:
        """Indentifies if a given list of tiles has unique values."""
        
        # Get a list of the values of non-empty tiles
        present_values = list(filter(lambda value: value > 0, list(map(lambda tile: tile.value, tiles))))

        # Perform an efficient search to check if the found values are unique. If not, then the tiles are invalid.
        for i, val in enumerate(present_values):
            for check_val in present_values[(i+1):]:
                if val == check_val: return False
        return True
    
    def check_if_valid(self) -> bool:
        """Identifies if the current board configuration is valid, by checking each row, column and square has unique values."""
        for row in self.get_rows():
            if not self.valid_tiles(row): return False
        for column in self.get_columns():
            if not self.valid_tiles(column): return False
        for square in self.get_squares():
            if not self.valid_tiles(square): return False
        
        return True
        
    def check_if_filled(self) -> bool:
        """Check if the puzzle is filled in its current state."""

        for tile in self.get_tiles():
            if not tile.is_filled(): return False
        return True


    def prune_tiles(self, tiles: list[Tile]):
        """Reduce state space of tiles given what values are present in 'tiles'."""
        for tile in tiles:
            # If a tile is not filled, then reduce its state space by the other values that appear in 'tiles'.
            if not tile.is_filled():
                for check_tile in tiles:
                    try: tile.states.remove(check_tile.value)
                    except: pass

    def prune_board(self):
        """Prunes all rows, columns and squares of the board."""
        for row in self.get_rows():
            self.prune_tiles(row)
        for column in self.get_columns():
            self.prune_tiles(column)
        for square in self.get_squares():
            self.prune_tiles(square)


    def collapse(self):
        """Collapse tiles (fill in if only one value is possible) and identify unsolvability."""
        for tile in self.get_tiles():
            # If the tile is currently unfilled but there is only one possible value for it, assign this value.
            if (not tile.is_filled()) and len(tile.states) == 1:
                tile.value = tile.states[0]
                self.state_changed = True

    def branch(self):
        """When pruning becomes ineffective, branch the puzzle: choose an unfilled tile and explore all possibilities."""

        # Identify a tile to branch from as the first tile with the smallest state space among all unfilled tiles.
        unfilled_states = [tile.states for tile in self.get_tiles(lambda tile: len(tile.states) > 1)]
        min_state_space = min(list(map(lambda space: len(space), unfilled_states)))
        branch_tile = list(filter(lambda tile: len(tile.states) == min_state_space, self.get_tiles()))[0]

        # Attempt to solve the puzzle when the branch tile is collapsed into each of its possible states.
        for state in branch_tile.states:
            new_puzzle = copy.deepcopy(self)
            new_puzzle.fill_tile(state, branch_tile.position)
            new_puzzle.solve()

            if new_puzzle.check_if_filled() and new_puzzle.check_if_valid():
                self.board = new_puzzle.board
                break

    def solve(self) -> Puzzle:
        """Loop to solve the puzzle. Prunes possible states, and branches when necessary."""
        while (not self.check_if_filled()) and self.is_solvable:
            self.prune_board()
            self.collapse()

            self.is_solvable = self.check_if_valid()
            if not self.is_solvable: return None

            # If pruning has become ineffective (no change has occoured), begin a branch.
            if not self.state_changed:
                self.branch()
                return self

            self.state_changed = False


def solve_puzzle(name: str, config: list[str]):
    """Find a solution to a given puzzle configuration. Outputs the first one it finds, if any."""
    puzzle = Puzzle(config)
    print(f"Solving puzzle: {name}.")
    print(puzzle, "\n")

    start_time = time.time()
    puzzle.solve()
    
    if puzzle.is_solvable:
        print(f"Puzzle sovled! Time taken: {round(time.time() - start_time, 4)}s.")
        print(puzzle, "\n\n")
    else:
        print(f"Puzzle is unsolvable!\n\n")


easy = ("Easy", ["    345  ",
        "  89   3 ",
        "3    2789",
        "2 4  6815",
        "    4    ",
        "8765  4 2",
        "7523    6",
        " 1   79  ",
        "  942    "])

medium = ("Medium", ["   4 6 9 ",
          "     3  5",
          "45     86",
          "6 2 74  1",
          "    9    ",
          "9  56 7 8",
          "71     64",
          "3  6     ",
          " 6 9 2   "])

hard = ("Hard (requires branching)", ["9 3  42  ",
        "4 65     ",
        "  28     ",
        "     5  4",
        " 67 4 92 ",
        "1  9     ",
        "     87  ",
        "     94 3",
        "  83  6 1"])

evil = ("Evil (requires more branching)", ["  9      ",
        "384   5  ",
        "    4 3  ",
        "   1  27 ",
        "2  3 4  5",
        " 48  6   ",
        "  6 1    ",
        "  7   629",
        "     5   "])

for config in [easy, medium, hard, evil]:
    solve_puzzle(config[0], config[1])