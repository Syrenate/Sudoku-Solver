import time, csv
from Board import Board

# TO BE DONE: Random puzzle generator, GUI to interact with the puzzle.

def solveBoard(board: Board):
    board_stack = [board]

    while len(board_stack) > 0:
        head = board_stack.pop()

        try: head.solve()
        except: continue

        if head.isSolved(): return head

        branches = head.branch()
        if len(branches) > 0:
            for branch in branches:
                board_stack.append(branch)
        

    return None


def solvePuzzle(name: str, board: Board):    
    print(f"\nSolving puzzle: {name}. \n{board}\n")

    start_time = time.time()
    solution = solveBoard(board)
    
    if solution != None:
        print(f"Puzzle solved! Time taken: {round((time.time() - start_time) * 1000, 2)}ms. \n{solution}\n")
    else:
        print("Puzzle is unsolvable!\n\n")



if __name__ == "__main__":
    board = Board.getRandomPuzzle(10)


    if False:
        try:
            with open("src/test_puzzles.csv", newline="\n") as file:
                reader = csv.reader(file, delimiter='|')

                for file_config in reader: 
                    board = Board(file_config[1].split(","))
                    solvePuzzle(file_config[0], board)

        except ValueError as e:
            print(f"Invalid config. Reason: {e}\n")

        except OSError as e: 
            print(f"{e} (Is 'test_puzzles.csv' present and permissable in the current directory?)")