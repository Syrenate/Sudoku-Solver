import time, csv
from Puzzle import Puzzle

# TO BE DONE: Random puzzle generator, GUI to interact with the puzzle.

def check_config(user_config: str):
    """Identify whether or not a passed board configuration is valid (i.e. contains a grid of 3x3 squares.)"""
    config = user_config.split(",")

    if len(user_config) != 89 or len(config) != 9: 
        raise ValueError("invalid config (should be 9 blocks of 9 characters, each delimited by a comma).")

    if len(config) % 3 != 0:
        raise ValueError("invalid row count.")

    
    valid_chars = ['.',' ','0'] + list(map(lambda num: str(num), range(1,10)))

    for row_index, row in enumerate(config):
        if len(row) != 9: raise ValueError(f"invalid row size at row {row_index+1}.")

        for char in row:
            if not (char in valid_chars):
                raise ValueError(f"row {row_index+1} contains {char}, an invalid tile.")
            
    return config


def solve_puzzle(name: str, passed_config: list[str]):
    """Find a solution to a given puzzle configuration. Outputs the first one it finds, if any."""
    config = check_config(passed_config)
    puzzle = Puzzle(config)

    print(f"\nSolving puzzle: {name}. \n{puzzle}\n")

    start_time = time.time()
    puzzle.solve()
    
    if puzzle.is_solvable:
        print(f"Puzzle sovled! Time taken: {round((time.time() - start_time) * 1000, 2)}ms. \n{puzzle}\n")
    else:
        print("Puzzle is unsolvable!\n\n")





if __name__ == "__main__":
    running = True
    while running:
        user_input = input("Would you like to: \n\t[A] Solve your own puzzle.\n\t[B] Solve test puzzles.\n\t[C] Exit program.\n").upper()
        
        match(user_input):
            case 'A':
                ask_for_config = True
                
                while ask_for_config:
                    user_config = input("""Enter a puzzle configuration. (Format: rows seperated by commas, denoting empty squares by '.', '0', or ' '. Any board size (composed of 3x3 squares) is valid.)
                            I.e: (  9      ,384   5  ,    4 3  ,   1  27 ,2  3 4  5, 48  6   ,  6 1    ,  7   629,     5   ) To go back, type 'b'. \n""")
                    
                    if user_config.upper() == "B": ask_for_config = False
                    else:
                        try:
                            solve_puzzle("your puzzle", user_config)
                            ask_for_config = False
                        except ValueError as e:
                            print(f"Invalid config. Reason: {e}\n")

            case 'B':
                try:
                    with open("src/test_puzzles.csv", newline="\n") as file:
                        reader = csv.reader(file, delimiter='|')
                        for file_config in reader: 
                            solve_puzzle(file_config[0], file_config[1])
                except ValueError as e:
                    print(f"Invalid config. Reason: {e}\n")
                except OSError as e: 
                    print(f"{e} (Is 'test_puzzles.csv' present and permissable in the current directory?)")

            case 'C':
                running = False

            case _:
                print("Invalid option. Choose a letter corresponding to an option.\n")