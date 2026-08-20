from copy import deepcopy
from math import floor
import time

### Version 2
# Main problem with V1 was the absurd lack of attention to readability and a coherent structure. 
# So when branching didnt work, it was a clusterfuck to debug. Won't make that mistake again.

class BoardNode:
    def __init__(self, board: Board):
        self.board = board
        self.next = None

class BoardStack:
    def __init__(self, board: Board):
        self.head = BoardNode(board)
        self.size = 1

    def push(self, board: Board):
        prev_head = self.head
        new_head = BoardNode(board)

        if self.size > 0:
            new_head.next = prev_head
        
        self.head = new_head
        self.size += 1

    def pop(self):
        if self.size == 0:
            raise KeyError("Stack is empty!")

        head = self.head
        self.head = head.next

        self.size -= 1
        return head.board

    def peek(self):
        return self.head.board

    def isEmpty(self):
        return self.size == 0


        


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
        board = Board(config)
        self.stack = BoardStack(board)

        # Solvability tracking
        self.is_solved = False     
        self.is_solvable = True
        self.state_changed = False

    def __str__(self): 
        return str(self.stack.peek())


    ### Solving Methods

    def solve(self) -> bool:
        """Loop to solve the puzzle. Prunes possible states, and branches when the board becomes invariant under pruning.
            Output:
                Puzzle instance, partially filled if no solution is found."""

        while not self.stack.isEmpty():
            pass

        return False

        
        while (not self.check_if_filled()) and self.is_solvable:
            self.prune_board() # Reduce state space of all tiles accoring to the rules of Sudoku.
            self.collapse()    # Fill any tile for which only one possible state remains.

            self.is_solvable = self.check_if_valid()
            print(self.is_solvable)
            if not self.is_solvable: return False

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
    def __init__(self, value: str, row: int, column: int):
        if value in ['.', '0', ' ']:
            self.value = -1
            self.states = [True] * 9        # self.states = possible states of the tile (i.e. states[n] == tile could be 'n')
            self.possible_states = 9
        else:
            self.value = int(value)-1
            self.states = [False] * 9
            self.states[self.value] = True
            self.possible_states = 1

        self.row = row
        self.column = column

    def __str__(self): 
        return str(self.value+1) if self.isCollapsed() else '.'

    def isCollapsed(self) -> bool: 
        return self.possible_states == 1

    def collapseState(self, state: int):
        if self.states[state]:
            self.states[state] = False
            self.possible_states -= 1

            if self.isCollapsed(): 
                for i in range(9):
                    if self.states[i]: self.value = i

    def getSquareIndex(self) -> int:
        return 3 * floor(self.row / 3) + floor(self.column / 3);

class Board:
    """Board stores a given board configuration by a 2 dimensional array of Tiles, containing methods to extract data from the board. \n
        Input: 
            config: array of strings, representing an array of the lines present in the passed configuration.
        Properties:
            board_state: list of list of tiles, representing the list of rows of tiles on the board.
            size: Vector2, stores the dimensions of the board.
            square_count: Vector2, stores the number of squares on the board."""
    def __init__(self, config: list[str]):
        self.tiles : list[list[Tile]] = []
        self.rows     : list[list[bool]] = []
        self.columns  : list[list[bool]] = []
        self.squares  : list[list[bool]] = []

        for x in range(9):
            self.rows.append([])
            self.columns.append([])
            self.squares.append([])
            for y in range(9):
                self.rows[x].append(False)
                self.columns[x].append(False)
                self.squares[x].append(False)

        self.collapsed_tiles = 0
        self.state_changed = True

        for row, line in enumerate(config):
            tile_line = []
            for column, value in enumerate(line):
                tile = Tile(value, row, column)
                if tile.isCollapsed():
                    self.rows[row][tile.value]                      = True
                    self.columns[column][tile.value]                = True
                    self.squares[tile.getSquareIndex()][tile.value] = True

                    self.collapsed_tiles += 1

                tile_line.append(tile)
            self.tiles.append(tile_line)


    def solve(self):
        iteration = 10
        state_changed = True
        while (state_changed and self.collapsed_tiles < 81 and iteration > 0):
            state_changed = self.collapseTiles()
            print(state_changed, self.collapsed_tiles, "\n")
            print(self)

            time.sleep(0.5)
            iteration -= 1


    def collapseTiles(self):
        state_changed = False

        for row_index in range(9):
            for column_index in range(9):
                tile = self.tiles[row_index][column_index]

                if not tile.isCollapsed():
                    for state in range(0,9):
                        if self.rows[row_index][state] or \
                           self.columns[column_index][state] or \
                           self.squares[tile.getSquareIndex()][state]:
                            tile.collapseState(state)

                    if tile.possible_states < 1:
                        return False
                    
                    if tile.isCollapsed():
                        state_changed = True
                        self.collapsed_tiles += 1

                        self.rows[tile.row][tile.value]              = True
                        self.columns[tile.column][tile.value]        = True
                        self.rows[tile.getSquareIndex()][tile.value] = True
                    

        return state_changed
                    

    def __str__(self): 
        output = ""

        for j in range(9):
            line = ""
            for i in range(9):
                column_divider = " | " if (i+1) % 3 == 0 and i != 9 - 1 else " "
                line += str(self.tiles[j][i]) + column_divider

            line_break = '\n' if j != 9 - 1 else ''
            row_divider = ('-' * (9*2 + 3)) + '\n' if (j+1) % 3 == 0 and j != 9 - 1 else ''

            output += line + line_break + row_divider
        return output + "\n"
    
if __name__ == "__main__":
    board = Board("    345  ,  89   3 ,3    2789,2 4  6815,    4    ,8765  4 2,7523    6, 1   79  ,  942    ".split(","))
    print(board)
    board.solve()
    print(board)