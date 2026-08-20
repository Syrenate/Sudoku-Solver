from copy import deepcopy
from math import floor
from BoardStructure import Board, Tile, Vector2

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
        board = Board(config)
        self.board_stack = BoardStack(board)
        print(board)
        print(self.board_stack)

        # Solvability tracking
        self.is_solved = False     
        self.is_solvable = True
        self.state_changed = False

    def __str__(self): 
        return str(self.board())

    def board(self):
        return self.board_stack.head.board


    ### Solving Methods

    def solve(self) -> bool:
        """Loop to solve the puzzle. Prunes possible states, and branches when the board becomes invariant under pruning.
            Output:
                bool: whether a solution is found or not."""

        while not self.board_stack.is_empty():
            ## Prune the board until no change occours, in which case the board is either solved, or a guess must be made (and branching ensues).
            while True:
                print(self.board())
                print("\n")
                self.state_changed = False
                self.prune_board()
                print(self.state_changed)

                if not self.is_valid():
                    print("pop")
                    self.board_stack.pop()
                    break

                if self.is_filled():
                    print("solved")
                    return True
                
                if not self.state_changed:
                    print("branch")
                    self.branch()
                
        return False
    

    def branch(self):
        """When pruning becomes ineffective, branch the puzzle: (wisely) choose an unfilled tile and explore all possibilities."""

        branch_tile = None
        for tile in self.board().get_tiles():
            if not tile.is_filled() and not self.board_stack.head.has_branched(tile.position):
                branch_tile = tile
                break

        if branch_tile == None:
            self.board_stack.pop()
            return None

        self.board_stack.head.add_branch(branch_tile.position)

        for state in branch_tile.states:
            new_board = deepcopy(self.board())
            new_board.fill_tile(state, branch_tile.position)

            self.board_stack.push(new_board, branch_tile.position.to_index())

    ### Pruning Methods

    def get_present_values(self, tiles: list[Tile]):
        """Returns a list of the values that appear in (filled) tiles from the passed array."""
        filled_tiles = list(filter(lambda tile: tile.is_filled(), tiles))
        value_list = list(map(lambda tile: tile.value(), filled_tiles))
        return list(filter(lambda value: value > 0, value_list))

    def prune_tiles(self, tiles: list[Tile]):
        """Reduce state space of tiles based what values appear in the passed list of tiles."""
        present_values = self.get_present_values(tiles)

        for tile in tiles:
            # If a tile is not filled, then reduce its state space by the other values that appear in 'tiles'.
            if not tile.is_filled():
                for apparent_value in present_values:
                    try: tile.states.remove(apparent_value)
                    except: pass

                if tile.is_filled():
                    self.state_changed = True
                elif len(tile.states) == 0:
                    return False
        return True

    def prune_board(self):
        """Prunes all rows, columns and squares of the board, reducing the state space of all present tiles depending on the values that appear in that list."""
        for tile_region in self.board().get_sudoku_regions():
            valid_region = self.prune_tiles(tile_region)
            if not valid_region: return False
        return True


    ### Validity Checking Methods
        
    def is_filled(self) -> bool:
        """Check if all tiles have collapsed to a single value."""
        for tile in self.board().get_tiles():
            if not tile.is_filled(): return False
        return True
    

    def valid_tiles(self, tiles: list[Tile]) -> bool:
        """Indentifies if a given list of tiles has unique values."""

        # Check that all tiles have at least one possible state.
        for tile in tiles:
            if len(tile.states) > 0: return False

        # Perform an efficient search to check if the found values are unique. If not, then the tiles are invalid.
        present_values = self.get_present_values(tiles)
        for i, val in enumerate(present_values):
            for check_val in present_values[(i+1):]:
                if val == check_val: return False

        return True
    
    def is_valid(self) -> bool:
        """Identifies if the stack head is valid accoring to the rules of Sudoku. If not, the stack head is unsolvable."""
        for tile_region in self.board().get_sudoku_regions():
            if not self.valid_tiles(tile_region): return False
        
        return True

    ### Utility

    def clear_board(self):
        """Return the current instance of Puzzle to an empty state (an empty Board instance)."""
        size = self.board.size
        empty_config = ['0' * size.x] * size.y

        board = Board(empty_config)
        self.board_stack = BoardStack(board)


class BoardNode:
    def __init__(self, board: Board = None, branch_from: int = -1):
        self.branch_from = branch_from
        self.board = board
        self.next = None

        self.branches = []

    def __str__(self):
        output = f"({self.branch_from})"
        if self.branches == []:
            output += "None"
        else: output += str(self.branches)
        return output 

    def add_branch(self, pos: Vector2):
        """Record an explored branch so that it isn't explored again."""
        position_index = pos.to_index()
        self.branches.append(position_index)

    def has_branched(self, pos: Vector2):
        """Examine if a branch has been explored at the given position."""
        position_index = pos.to_index()
        return position_index in self.branches

class BoardStack:
    def __init__(self, board: Board = None):
        self.head = BoardNode(board)
        self.size = 0 if board == None else 1

    def __str__(self):
        current = self.head
        print(current)
        output = str(current) + ", "
        while current.next != None:
            current = current.next
            output += str(current)+ ", "
        return output

    def pop(self):
        if self.head == None:
            raise ValueError("Stack is empty!")

        stack_head = self.head
        self.head = stack_head.next
        self.size -= 1

        return stack_head.board

    def push(self, board: Board, branch_from: int):
        board_node = BoardNode(board, branch_from)
        board_node.next = self.head
        self.head = board_node
        self.size += 1

    def is_empty(self):
        return self.size == 0
