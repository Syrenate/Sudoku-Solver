import csv, time

from src.Solver import Board, solveBoard

def testSolver(): 
    with open("res/test_puzzles.csv", newline="\n") as file:
        reader = csv.reader(file, delimiter='|')

        for file_config in reader: 
            board = Board(file_config[1].split(","))

            print(f"Solving board: {file_config[0]}")
            print(board)

            start_time = time.time()
            solution = solveBoard(board)

            if solution == None:
                print("No solution found!")
            else:
                print(f"Puzzle solved! Time taken: {round((time.time() - start_time) * 1000, 2)}ms. \n{solution}\n")