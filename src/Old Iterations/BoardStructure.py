from math import floor

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

    def to_index(self):
        """Returns a unique integer corresponding to a position on the Sudoku board."""
        return self.y + 9 * self.x

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
            self.states = list(range(1, 1 + max(board_size.x, board_size.y)))
        else:
            self.states = [int(value)]
        self.position = pos

    def __str__(self): 
        return str(self.value()) if self.is_filled() else '.' if len(self.states) > 1 else '!'

    def is_filled(self) -> bool: 
        return len(self.states) == 1
    
    def value(self) -> int:
        if not self.is_filled():
            raise ValueError("Unfilled tile!")
        else: return self.states[0]

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
    
    def is_valid(self) -> bool:
        """Identifies if the current board configuration is valid accoring to the rules of Sudoku. If not, it is unsolvable."""
        for tile_region in self.get_sudoku_regions():
            if not self.valid_tiles(tile_region): return False
        
        return True

    def valid_tiles(self, tiles: list[Tile]) -> bool:
        """Indentifies if a given list of tiles has unique values."""
        present_values = self.get_present_values(tiles)

        # Perform an efficient search to check if the found values are unique. If not, then the tiles are invalid.
        for i, val in enumerate(present_values):
            for check_val in present_values[(i+1):]:
                if val == check_val: return False
        return True

    def get_present_values(self, tiles: list[Tile]):
        """Returns a list of the values that appear in (filled) tiles from the passed array."""
        filled_tiles = list(filter(lambda tile: tile.is_filled(), tiles))
        return list(map(lambda tile: tile.value(), filled_tiles))
    

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