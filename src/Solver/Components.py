from math import floor

class Region:
    ## Region stores the state of a row, column or square in the Sudoku board.
    ## Outside of Tile and Region, all values are considered 1-9 to correlate with a traditional Sudoku puzzle.

    def __init__(self):
        self.values = [False for i in range(9)]
        self.present_values = 0

    def __str__(self):
        output = ""
        for i in range(1,10): 
            output += "1" if self.contains(i) else "0"
        return output

    def addValue(self, value: int):
        if self.values[value-1] == False:
            self.values[value-1] = True
            self.present_values += 1

    def contains(self, value: int):
        return self.values[value-1]


class Tile:
    def __init__(self, row: int, column: int, value: str):
        self.row = row
        self.column = column
        self.square = 3 * floor(row / 3) + floor(column / 3)

        is_empty = value in ['.', '0', ' ']

        self.possible_values = 9 if is_empty else 1
        self.states = [(True if is_empty else (i == int(value))) for i in range(1, 10)]


    def __str__(self): 
        return str(self.getValue()) if self.isCollapsed() else '.'

    def isCollapsed(self) -> bool: 
        return self.possible_values == 1

    def couldBe(self, value: int) -> bool:
        return self.states[value-1]
    
    def reduceState(self, value: int) -> bool:
        if self.states[value-1] and not self.isCollapsed():
            self.states[value-1] = False
            self.possible_values -= 1

            if self.isCollapsed():
                return True
        return False


    def getValue(self) -> int:
        if self.isCollapsed(): 
            for value in range(1, 10):
                if self.states[value-1]: return value
        return 0