from copy import deepcopy
from math import floor

### Version 2
# Main problem with V1 was the absurd lack of attention to readability and a coherent structure. 
# So when branching didnt work, it was a clusterfuck to debug. Won't make that mistake again.


class Puzzle:
    """A puzzle creates a Board using a given config, containing methods to find a solution.\n
        Input: 
            config: list of strings, representing the rows of the board configuration.
        Properties:
            board: Board, initialised accoring to the passed configuration.
            is_solved: bool, tracks if the puzzle is solved or not.
            is_solvable: bool, tracks whether a solution could be attained from the current state. Used to determine if the puzzle should be abandoned and deemed unsolvable.
            state_changed: bool, tracks if an iteration has changed the board. Used to determine if the board cannot be filled any further (i.e. due to missing information)."""
    
    def __init__(self, config: list[str]):
        self.board = Board(config)

        # Solvability tracking
        self.is_solved = False     
        self.is_solvable = True
        self.state_changed = False

    def __str__(self): 
        return str(self.board)


    ### Solving Methods

    def solve(self) -> Puzzle:
        """Loop to solve the puzzle. Prunes possible states, and branches when the board becomes invariant under pruning.
            Output:
                Puzzle instance, partially filled if no solution is found."""
        while (not self.check_if_filled()) and self.is_solvable:
            self.prune_board() # Reduce state space of all tiles accoring to the rules of Sudoku.
            self.collapse()    # Fill any tile for which only one possible state remains.

            self.is_solvable = self.check_if_valid()
            if not self.is_solvable: return None

            # If pruning has become ineffective (no change has occoured), begin a branch.
            if not self.state_changed:
                self.branch()
                return self

            self.state_changed = False

    def collapse(self):
        """Collapse tiles (fill in if only one value is possible)."""
        for tile in self.board.get_tiles():
            # If the tile is currently unfilled but there is only one possible value for it, assign this value.
            if (not tile.is_filled()) and len(tile.states) == 1:
                tile.value = tile.states[0]
                self.state_changed = True

    def branch(self):
        """When pruning becomes ineffective, branch the puzzle: (wisely) choose an unfilled tile and explore all possibilities."""

        # Identify a tile to branch from as the first tile with the smallest state space among all unfilled tiles.
        unfilled_states = [tile.states for tile in self.board.get_tiles(lambda tile: len(tile.states) > 1)]
        min_state_space = min(list(map(lambda space: len(space), unfilled_states)))
        branch_tile = list(filter(lambda tile: len(tile.states) == min_state_space, self.board.get_tiles()))[0]

        # Attempt to solve the puzzle when the branch tile is collapsed into each of its possible states.
        for state in branch_tile.states:
            new_puzzle = deepcopy(self)
            new_puzzle.board.fill_tile(state, branch_tile.position)
            new_puzzle.solve()

            if new_puzzle.check_if_filled() and new_puzzle.check_if_valid():
                self.board = new_puzzle.board
                break

    ### Pruning Methods

    def get_present_values(self, tiles: list[Tile]):
        """Returns a list of the values that appear in (filled) tiles from the passed array."""
        value_list = list(map(lambda tile: tile.value, tiles))
        return list(filter(lambda value: value > 0, value_list))

    def valid_tiles(self, tiles: list[Tile]) -> bool:
        """Indentifies if a given list of tiles has unique values."""
        present_values = self.get_present_values(tiles)

        # Perform an efficient search to check if the found values are unique. If not, then the tiles are invalid.
        for i, val in enumerate(present_values):
            for check_val in present_values[(i+1):]:
                if val == check_val: return False
        return True

    def prune_tiles(self, tiles: list[Tile]):
        """Reduce state space of tiles based what values appear in the passed list of tiles."""
        present_values = self.get_present_values(tiles)

        for tile in tiles:
            # If a tile is not filled, then reduce its state space by the other values that appear in 'tiles'.
            if not tile.is_filled():
                for apparent_value in present_values:
                    try: tile.states.remove(apparent_value)
                    except: pass

    def prune_board(self):
        """Prunes all rows, columns and squares of the board, reducing the state space of all present tiles depending on the values that appear in that list."""
        for tile_region in self.board.get_sudoku_regions():
            self.prune_tiles(tile_region)


    ### Validity Checking Methods
        
    def check_if_filled(self) -> bool:
        """Check if the puzzle is filled in its current state."""
        for tile in self.board.get_tiles():
            if not tile.is_filled(): return False
        return True
    
    def check_if_valid(self) -> bool:
        """Identifies if the current board configuration is valid accoring to the rules of Sudoku. If not, the most recent branch was unsucessful."""
        for tile_region in self.board.get_sudoku_regions():
            if not self.valid_tiles(tile_region): return False
        
        return True

    ### Utility

    def clear_board(self):
        """Return the current instance of Puzzle to an empty state (an empty Board instance)."""
        size = self.board.size
        empty_config = ['0' * size.x] * size.y
        self.board = Board(empty_config)


##  Board Structure Classes

class Vector2:
    """A 2 dimensional vector. \n
        Input:
            x: int, horizontal position (left to right)
            y: int, vertical position (top to bottom)"""
    def __init__(self, x: int, y: int):
        self.x = x; self.y = y
    def __str__(self): return f"({self.x}, {self.y})"
    def ZERO(): return Vector2(0, 0)

class Tile:
    """Class representing a board piece. \n
        Input:
            value: string, what is found in the board configuration.
            pos: Vector2, position of the tile in the board (starting at (0,0))
        Properties:
            value: integer state of the tile.
            states: array of possible values the tile may have. initially all values if the tile is not already filled."""
    def __init__(self, value: str, pos: Vector2, board_size: Vector2):
        if value in ['.', '0', ' ']:
            self.value = 0
            self.states = list(range(1, 1 + max(board_size.x, board_size.y)))
        else:
            self.value = int(value)
            self.states = [self.value]
        self.position = pos

    def __str__(self): 
        return str(self.value) if self.is_filled() else '.'

    def is_filled(self) -> bool: 
        return self.value != 0

class Board:
    """Board stores a given board configuration by a 2 dimensional array of Tiles, containing methods to extract data from the board. \n
        Input: 
            config: array of strings, representing an array of the lines present in the passed configuration.
        Properties:
            board_state: list of list of tiles, representing the list of rows of tiles on the board.
            size: Vector2, stores the dimensions of the board.
            square_count: Vector2, stores the number of squares on the board."""
    def __init__(self, config: list[str]):
        self.config = config
        self.size = Vector2(len(config[0]), len(config))
        self.square_count = Vector2(floor(self.size.x / 3), floor(self.size.y / 3))

        self.board_state = []
        for j, line in enumerate(config):
            tile_line = [Tile(value, Vector2(i,j), self.size) for i, value in enumerate(line)]
            self.board_state.append(tile_line)

            
    def __str__(self): 
        output = ""

        for j in range(self.size.y):
            line = ""
            for i in range(self.size.x):
                value = str(self.get_tile(Vector2(i,j)))
                column_divider = " | " if (i+1) % 3 == 0 and i != self.size.x - 1 else " "
                line += (value if value != '0' else '.') + column_divider

            line_break = '\n' if j != self.size.y - 1 else ''
            row_divider = ('-' * (self.size.x*2 + self.square_count.x)) + '\n' if (j+1) % 3 == 0 and j != self.size.y - 1 else ''

            output += line + line_break + row_divider
        return output 

    def fill_tile(self, value: int, pos: Vector2):
        """Replace a tile at a specified position with a specified value."""
        self.board_state[pos.y][pos.x] = Tile(value, pos, self.size)
    

    ### Board Searching Methods

    def get_tile(self, pos: Vector2) -> Tile:
        """Returns the tile at a given position"""
        return self.board_state[pos.y][pos.x]
    
    def get_rows(self) -> list[list[Tile]]:
        """Returns the rows of the board."""
        return self.board_state
    
    def get_columns(self) -> list[list[Tile]]:
        """Returns the columns of the board."""
        columns = []
        for i in range(self.size.x):
            column = [self.get_tile(Vector2(i,j)) for j in range(self.size.y)]
            columns.append(column)
        return columns
    
    def get_squares(self) -> list[list[Tile]]:
        """Returns all squares on the board (each 3x3 cell of tiles)."""
        squares = []
        # Loop through the top-left corner of each square.
        for i0 in range(self.square_count.x):
            for j0 in range(self.square_count.y):
                square = []

                # Loop through each tile in the current square.
                for i in range(i0*3, (i0+1)*3):
                    for j in range(j0*3, (j0+1)*3):
                        square.append(self.get_tile(Vector2(i,j)))
                squares.append(square)

        return squares

    def get_sudoku_regions(self) -> list[list[Tile]]:
        """Return all rows, columns and squares on the board accoring to the rules of Sudoku."""
        return self.get_rows() + self.get_columns() + self.get_squares()
    
    def get_tiles(self, condition = (lambda x: x)) -> list[Tile]:
        """Returns all tiles in the board that satisfy a specified condition on each tile."""
        tiles = []
        for i in range(self.size.x):
            for j in range(self.size.y):
                tile = self.get_tile(Vector2(i,j))
                if condition(tile):
                    tiles.append(tile)
        return tiles