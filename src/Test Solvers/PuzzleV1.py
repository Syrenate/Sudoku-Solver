import time

### Version 1
### THIS DOES NOT WORK

class Tile:
    def __init__(self, value):
        self.filled = False if value == '0' or value == '.' or value == ' ' else True
        self.value = 0
        self.states = []
        if self.filled: self.value = int(value)
        else: self.states = list(range(1,10))

    def __str__(self): 
        return str(self.value)

    def empty(): return Tile(0)


class BoardState:
    def __init__(self, config: list[str]):
        self.board = []
        for row in config:
            line = []
            for i in range(9):
                value = row[i]
                line.append(Tile(value))
            self.board.append(line)
    
    def __str__(self): 
        output = ""
        for j in range(9):
            line = ""
            for i in range(9):
                value = str(self.board[j][i])
                line += (value if value != '0' else '.') + (" | " if (i+1) % 3 == 0 and i != 8 else " ")
            output += line + ('\n' if j != 8 else '') + (('-' * 21) + '\n' if (j+1) % 3 == 0 and j != 8 else '')
        return output 

    def board_to_config(self):
        config = []
        for row in self.board:
            line = ""
            for tile in row: line += str(tile.value)
            config.append(line)
        return config


class Board:
    def __init__(self, config):
        """Create a board with a given configuration, a list of rows of the puzzle where '0', '.' and ' ' denote empty spaces."""
        self.board_state = BoardState(config)

        self.changed_state = False
        self.is_solved = False
        self.is_solvable = True

    def __str__(self): 
        return str(self.board_state)

    def evaluate(self):
        """Check if the board is solved, updating is_solved."""
        self.is_solved = True
        for row in self.board_state.board:
            for tile in row:
                if not tile.filled: 
                    if len(tile.states) == 0:
                        self.is_solvable = False
                    self.is_solved = False


    def collapse(self):
        for j in range(9):
            for i in range(9):
                tile = self.board_state.board[j][i]
                if not tile.filled:
                    if len(tile.states) == 0:
                        self.is_solvable = False
                        break
                    elif len(tile.states) == 1:
                        tile.value = tile.states[0]
                        tile.states = []
                        tile.filled = True
                        self.changed_state = True

    def prune_tiles(self, tiles: list[Tile]):
        """Prune tiles in a given list of tiles by eliminating common values."""
        present_digits = []
        for tile in tiles: 
            if tile.filled: present_digits.append(tile.value)
        
        for tile in tiles:
            if not tile.filled:
                for digit in present_digits:
                    try: tile.states.remove(digit)
                    except: pass

    def prune_row(self, j: int):
        """Prune a row given a row index. Must be between 0 and 8 inclusive."""
        row = self.board_state.board[j]
        self.prune_tiles(row)

    def prune_column(self, i: int):
        """Prune a column given a row index. Must be between 0 and 8 inclusive."""
        column = [self.board_state.board[j][i] for j in range(9)]
        self.prune_tiles(column)

    def prune_square(self, i: int, j: int):
        """Prune a square given a row and column index. Must both be between 0 and 8 inclusive and be multiplies of 3 (when 1 is added)."""
        tiles = []
        for i0 in range(i, i+3):
            for j0 in range(j, j+3):
                tiles.append(self.board_state.board[j0][i0])
        self.prune_tiles(tiles)
        
    def prune_board(self):
        """Prune the entire board once."""
        for i in range(9): self.prune_column(i)
        for j in range(9): self.prune_row(j)

        for i in range(3):
            for j in range(3):
                self.prune_square(i*3, j*3)
        
        if self.is_solvable:
            self.collapse()


    def branch(self): # Doesnt work.
        """Consider solving multiple boards when board state does not change between prunes. Chooses a tile, and creates multiple boards based on possible states of the tile. Returns if a solution was found."""
        tiles = []
        states = []
        for j in range(9):
            for i in range(9):
                tile = self.board_state.board[j][i]
                tiles.append(tile)
                states.append(tile.states)

        if self.is_solvable:
            smallest_state_size = min(list(filter(lambda x: x > 1, list(map(lambda x: len(x), states)))))

            branch_index = -1
            for i, tile in enumerate(tiles):
                if not tile.filled: 
                    if len(tile.states) == smallest_state_size:
                        branch_index = i
                        break

            branch_i = branch_index % 9; branch_j = int((branch_index - branch_i) / 9)

            solvable = False
            for state in states[branch_index]:
                new_config = self.board_state.board_to_config()
                line = new_config[branch_j]
                new_config[branch_j] = line[:branch_i] + str(state) + line[(branch_i+1):]
                new_board = Board(new_config)

                new_board.solve()
                if new_board.is_solvable:
                    self.board_state = new_board.board_state
                    solvable = True
                    return True
                
            if solvable == False: self.is_solvable = False
            return False
        
    def solve(self):
        """Solve the board by repeatedly pruning, and branching when necessary. Ends when board is solved or is found to be unsolvable."""
        while not self.is_solved and self.is_solvable:
            self.prune_board()
            self.evaluate()

            print(self.board_state)
            print("\n")

            if not self.changed_state:
                print("Branching")
                self.branch()

            self.changed_state = False


def solve_board(starting_config: str):
    game_board = Board(starting_config)
    print("Puzzle configuration:")
    print(game_board)
    print("Solving...\n")

    start_time = time.time()
    game_board.solve()
    if game_board.is_solvable:
        print(f"Solved! Time taken: {time.time()-start_time}s")
    else: print("Board is not solvable!")
    print(game_board)   

test = ['903614200', '406500000', '002800000', '009005004', '067143920', '100900000', '000008700', '000009403', '008300601']

easy = ["    345  ",
        "  89   3 ",
        "3    2789",
        "2 4  6815",
        "    4    ",
        "8765  4 2",
        "7523    6",
        " 1   79  ",
        "  942    "]

medium = ["   4 6 9 ",
          "     3  5",
          "45     86",
          "6 2 74  1",
          "    9    ",
          "9  56 7 8",
          "71     64",
          "3  6     ",
          " 6 9 2   "]

hard = ["9 3  42  ",
        "4 65     ",
        "  28     ",
        "     5  4",
        " 67 4 92 ",
        "1  9     ",
        "     87  ",
        "     94 3",
        "  83  6 1"]

evil = ["  9      ",
        "384   5  ",
        "    4 3  ",
        "   1  27 ",
        "2  3 4  5",
        " 48  6   ",
        "  6 1    ",
        "  7   629",
        "     5   "]

solve_board(evil)