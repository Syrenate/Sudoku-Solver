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
    def __init__(self, row:int, col:int):
        self.row = row
        self.col = col

    def __str__(self):
        return f"({self.row},{self.col})"

    def nextTile(self):
        if self.row == 8 and self.col == 8: return self

        new_row = self.row + (1 if self.col == 8 else 0)
        new_col = (self.col + 1) % 9
        return Vector2(new_row, new_col)

class Orientation(Enum):
    VERTICAL = 0
    HORIZONTAL = 1
    INTERSECTION = 2


class BoardTile(QPushButton):
    def __init__(self, board: PuzzleBoard, row: int, col: int, init_label: str = " "):
        super().__init__()
        self.windowTitle="BoardTile"
        self.pos = Vector2(row, col)
        self.text = init_label
        self.board = board

        self.setFixedSize(QSize(50, 50))
        self.clicked.connect(self.change_target)

    def change_target(self):
        self.board.setTarget(self.pos)


class PuzzleBoard(QWidget):
    def __init__(self, parent:MainWindow, init_config = None):
        super().__init__()
        self.parent=parent
        self.config = ["         " for i in range(9)] if init_config == None else init_config

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
                        button = BoardTile(self, board_pos.row, board_pos.col)
                        button.setStyleSheet("background-color:white")
                        square_layout.addWidget(button, y, x)

                self.layout.addLayout(square_layout, row, column)
        self.setLayout(self.layout)

        self.displayConfig()

    def getTile(self, pos: Vector2):
        square_pos = Vector2(floor(pos.row/3), floor(pos.col/3))
        widget_square = self.layout.itemAtPosition(square_pos.row, square_pos.col).layout()
        widget_item = widget_square.itemAtPosition(pos.row % 3, pos.col % 3)
        return widget_item.widget()


    def addTile(self, pos: Vector2, value: str):
        row = self.config[pos.row]
        self.config[pos.row] = row[:pos.col] + value + row[pos.col+1:]
        self.displayTile(self.target, value)


    def displayTile(self, pos: Vector2, value: str):
        tile = self.getTile(pos)
        tile.setText(value)

    def displayConfig(self):
        for x, row in enumerate(self.config):
            for y, value in enumerate(row):
                self.displayTile(Vector2(x,y), value)
        

    def setTarget(self, pos: Vector2):
        if self.target != None:
            old_target_tile = self.getTile(self.target)
            old_target_tile.setStyleSheet("background-color:white")

        if pos != None:
            new_target_tile = self.getTile(pos)
            new_target_tile.setStyleSheet("background-color:qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #dddddd, stop: 1 #dddddd);")
            self.target = pos



    def SolveBoard(self):
        board = Board(self.config)
        solution = solveBoard(board)

        if solution != None: 
            self.config = solution.generateNewConfig()
            self.parent.addDebug("Solution found!", "green")
            self.parent
        else:
            self.parent.addDebug("No solution found!", "red")
        self.displayConfig()

    def ClearBoard(self):
        self.parent.addDebug("", "black")
        self.config = ["         " for i in range(9)]
        self.displayConfig()


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


        config = "  9      ,384   5  ,    4 3  ,   1  27 ,2  3 4  5, 48  6   ,  6 1    ,  7   629,     5   ".split(",")

        self.puzzle_board = PuzzleBoard(parent=self, init_config=config);         
        self.layout.addWidget(self.puzzle_board, 1, 0, alignment=Qt.AlignmentFlag.AlignJustify)

        self.puzzle_debug = QLabel(""); self.puzzle_debug.setObjectName("Debug")
        self.layout.addWidget(self.puzzle_debug, 2, 0, alignment = Qt.AlignmentFlag.AlignJustify)

        self.puzzle_interface = PuzzleInterface(parent=self); 
        self.layout.addWidget(self.puzzle_interface, 3, 0, alignment=Qt.AlignmentFlag.AlignJustify)
        
        holding_widget = QWidget()
        holding_widget.setLayout(self.layout)
        self.setCentralWidget(holding_widget)

    def keyPressEvent(self, event):
        text = event.text()
        backspace_event_key = 16777219

        if self.puzzle_board.target != None:
            try: 
                if int(text) in range(1, 10): 
                    self.puzzle_board.addTile(self.puzzle_board.target, text)
                    self.puzzle_board.setTarget(self.puzzle_board.target.nextTile())
            except:
                if event.key() == backspace_event_key: 
                    self.puzzle_board.addTile(self.puzzle_board.target, " ")

    def SolveBoard(self):
        self.puzzle_board.SolveBoard()

    def ClearBoard(self):
        self.puzzle_board.ClearBoard()

    def addDebug(self, text: str, color: str):
        self.puzzle_debug.setText(text)
        self.puzzle_debug.setStyleSheet(f"color:{color}")