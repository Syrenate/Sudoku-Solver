import csv, time

from src.Solver import Board, solveBoard

def timeMethod(base_fn):
    def timedMethod(name, config):
        start_time = time.time()
        base_fn(name, config)
        print(f"Time taken: {round((time.time() - start_time) * 1000, 2)}ms.\n\n")
    return timedMethod


@timeMethod
def solveFromConfig(name: str, config: list[str]):
    board = Board(config)

    print(f"Solving board: {name}")
    print(board, "\n")

    solution = solveBoard(board)
    if solution == None:
        print("No solution found!")
    else: print(solution)


def testSolver(): 
    with open("res/test_puzzles.csv", newline="\n") as file:
        reader = csv.reader(file, delimiter='|')

        for file_config in reader: 
            solveFromConfig(file_config[0], file_config[1].split(","))