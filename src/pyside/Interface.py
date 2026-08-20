from PySide6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QWidget, 
    QPushButton, 
    QLabel, 
    QGridLayout, 
    QMenuBar, 
    QMenu,
    QFrame,
    QVBoxLayout
)
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Slot, QObject, QEvent, QSize, Qt, QRect

from enum import Enum
from math import floor; 
import random, sys

from src.Solver import Board, Tile, solveBoard


class Vector2:
    def __init__(self, x:int, y:int):
        self.x = x
        self.y = y

class Orientation(Enum):
    VERTICAL = 0
    HORIZONTAL = 1
    INTERSECTION = 2


class BoardTile(QPushButton):
    def __init__(self, board: PuzzleBoard, x: int, y: int, init_label: str = " "):
        super().__init__()
        self.windowTitle="BoardTile"
        self.pos = Vector2(x, y)
        self.text = init_label
        self.board = board

        self.setFixedSize(QSize(50, 50))

        self.clicked.connect(self.change_target)

    def change_target(self):
        board = self.board
        if board.target == None or board.target != self.pos: 
            board.target = self.pos
        else: board.target = None


class PuzzleBoard(QWidget):
    def __init__(self, parent:MainWindow):
        super().__init__()
        self.parent=parent

        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(10)
        self.layout.setVerticalSpacing(10)

        self.target: Vector2 = None

        for row in range(3):
            for column in range(3):
                square_layout = QGridLayout()
                square_layout.setHorizontalSpacing(2)
                square_layout.setVerticalSpacing(2)

                for y in range(3):
                    for x in range(3):
                        board_pos = Vector2(3*row + y, 3*column + x)
                        button = BoardTile(self, board_pos.y, board_pos.x)
                        square_layout.addWidget(button, y, x)

                self.layout.addLayout(square_layout, row, column)

        self.setLayout(self.layout)

    def set_tile(self, pos: Vector2, value: int):
        square_pos = Vector2(floor(pos.x/3), floor(pos.y/3))
        widget_square = self.layout.itemAtPosition(square_pos.y, square_pos.x).layout()
        widget_item = widget_square.itemAtPosition(pos.y % 3, pos.x % 3)

        widget_item.widget().setText(str(value))
        new_config = self.parent.board.generateNewConfig(Tile(pos.y, pos.x, value))
        self.parent.board = Board(new_config)


    def keyPressEvent(self, event):
        print("Detected")
        text = event.text()
        backspace_event_key = 16777219

        new_text = None
        try: 
            if int(text) in range(1, 10): new_text = text
        except:
            if event.key() == backspace_event_key: new_text = " "

        target = self.target
        if target != None and new_text != None: 
            print(f"Setting {target} to {new_text}")
            self.set_tile(target, new_text)


class PuzzleInterface(QWidget):
    def __init__(self, parent: MainWindow):
        super().__init__()

        layout = QGridLayout()

        clear_button = QPushButton("Clear Board")
        clear_button.clicked.connect(parent.ClearBoard)
        layout.addWidget(clear_button, 0, 0)

        solve_button = QPushButton("Solve")
        solve_button.clicked.connect(parent.SolveBoard)
        layout.addWidget(solve_button, 0, 1)

        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()


        self.setMinimumHeight = 200; self.height = 500
        self.setMinimumWidth = 200;  self.width = 500

        self.setWindowTitle("Sudoku Solver")
        self.layout = QGridLayout()

        title = QLabel("Sudoku Solver"); title.setObjectName("Title")
        self.layout.addWidget(title, 0, 0, alignment=Qt.AlignmentFlag.AlignJustify)
        #title = QLabel("A python app by Lyric"); title.setObjectName("Description")
        #self.layout.addWidget(title, 1, 0, alignment=Qt.AlignmentFlag.AlignJustify)


        self.board = Board("  9      ,384   5  ,    4 3  ,   1  27 ,2  3 4  5, 48  6   ,  6 1    ,  7   629,     5   ".split(","))
        self.puzzle_board = PuzzleBoard(parent=self);         
        self.layout.addWidget(self.puzzle_board, 2, 0, alignment=Qt.AlignmentFlag.AlignJustify)
        self.puzzle_interface = PuzzleInterface(parent=self); 
        self.layout.addWidget(self.puzzle_interface, 3, 0, alignment=Qt.AlignmentFlag.AlignJustify)
        
        self.LoadBoard()
        holding_widget = QWidget()
        holding_widget.setLayout(self.layout)
        self.setCentralWidget(holding_widget)
        

    def LoadBoard(self):
        for y, row in enumerate(self.board.tiles):
            for x, tile in enumerate(row):
                tile_value = tile.getValue()
                print(f"({y},{x}): {tile_value}")

                tile_val = ' ' if tile_value == 0 else str(tile_value)
                self.puzzle_board.set_tile(Vector2(x,y), tile_val)

    def SolveBoard(self):
        solution = solveBoard(self.board)
        if solution != None: self.board = solution
        self.LoadBoard()

    def ClearBoard(self):
        self.board = Board.empty()
        self.LoadBoard()



if __name__ == "__main__":
    app = QApplication([])
    with open("res/style.qss", "r") as file:
        style = file.read()
        app.setStyleSheet(style)


    window = MainWindow()

    #window.LoadPuzzle(window.puzzle)

    window.show()
    app.exec()