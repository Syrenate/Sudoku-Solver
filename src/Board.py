from copy import deepcopy
from Components import Tile, Region
from random import randrange

### Version 2
# Main problem with V1 was the absurd lack of attention to readability and a coherent structure. 
# So when branching didnt work, it was a clusterfuck to debug. Won't make that mistake again.



class Board:
    """Board stores a given board configuration by a 2 dimensional array of Tiles, containing methods to extract data from the board. \n
        Input: 
            config: array of strings, representing an array of the lines present in the passed configuration.
        Properties:
            board_state: list of list of tiles, representing the list of rows of tiles on the board.
            size: Vector2, stores the dimensions of the board.
            square_count: Vector2, stores the number of squares on the board."""
    def __init__(self, config: list[str]):
        self.tiles: list[list[Tile]] = []
        self.collapsed_tiles = 0

        self.rows    = [Region() for i in range(9)]
        self.columns = [Region() for i in range(9)]
        self.squares = [Region() for i in range(9)]

        for row_index, line in enumerate(config):
            tile_line = []
            for column_index, value in enumerate(line): 
                tile = Tile(row_index, column_index, value)

                if tile.isCollapsed(): 
                    self.collapsed_tiles += 1
                    self.pruneRegions(tile)

                tile_line.append(tile)
            self.tiles.append(tile_line)

        self.pruneBoard()


    def __str__(self): 
        output = ""

        for j in range(9):
            line = ""
            for i in range(9):
                value = str(self.tiles[j][i])
                column_divider = " | " if (i+1) % 3 == 0 and i != 8 else " "
                line += (value if value != '0' else '.') + column_divider

            line_break = '\n' if j != 8 else ''
            row_divider = ('-' * 21) + '\n' if (j+1) % 3 == 0 and j != 8 else ''

            output += line + line_break + row_divider
        return output 

    

    def pruneRegions(self, tile: Tile):
        if tile.isCollapsed():
            tile_value = tile.getValue()

            self.rows[tile.row].addValue(tile_value)
            self.columns[tile.column].addValue(tile_value)
            self.squares[tile.square].addValue(tile_value)

    def isDuplicate(self, value: int, tile: Tile):
        return (self.rows[tile.row].contains(value) or self.columns[tile.column].contains(value) \
                                                    or self.squares[tile.square].contains(value) )

    def pruneTile(self, tile: Tile, value: int) -> bool:
        did_state_change = False

        if self.isDuplicate(value, tile) and not tile.isCollapsed():
            did_collapse = tile.reduceState(value)

            if did_collapse:
                collapsed_value = tile.getValue()
                if self.isDuplicate(collapsed_value, tile):
                    raise ValueError("Invalid board")

                did_state_change = True
                self.collapsed_tiles += 1
                self.pruneRegions(tile)


        return did_state_change

    def pruneBoard(self) -> bool:
        did_state_change = False

        for row_index in range(9):
            for col_index in range(9):
                tile = self.tiles[row_index][col_index]

                for value in range(9):
                    state_changed = self.pruneTile(tile, value)
                    if state_changed: did_state_change = True

        return did_state_change

    def isSolved(self):
        return self.collapsed_tiles == 81

    def solve(self) -> bool:
        state_changed = True
        while state_changed and not self.isSolved():
            state_changed = self.pruneBoard()

            if self.isSolved():
                return True

        return False


    def branch(self) -> list[Board]:
        for row_index in range(9):
            for col_index in range(9):
                tile = self.tiles[row_index][col_index]

                if not tile.isCollapsed():
                    return self.branchFrom(tile)
        return []

    def branchFrom(self, tile: Tile) -> list[Board]:
        branches: list[Board] = []

        for value in range(1,10): 
            if tile.couldBe(value): 
                new_board = deepcopy(self)
                new_tile = Tile(tile.row, tile.column, value)

                new_board.collapsed_tiles += 1
                new_board.tiles[new_tile.row][new_tile.column] = new_tile
                new_board.pruneRegions(new_tile)

                branches.append(new_board)

        return branches