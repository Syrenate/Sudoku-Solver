from PySide6.QtWidgets import QApplication
from src.pyside import MainWindow

if __name__ == "__main__":
    app = QApplication([])
    with open("src/pyside/ui_style.qss", "r") as file:
        style = file.read()
        app.setStyleSheet(style)


    window = MainWindow()

    #window.LoadPuzzle(window.puzzle)

    window.show()
    app.exec()