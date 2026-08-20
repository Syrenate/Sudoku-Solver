from test import testSolver

if __name__ == "__main__":
    user_input = input("What test would you like to conduct? \n\t[A] Solution finding on sample boards.\n")
    print("\n\n")
    
    match user_input.upper():
        case "A": testSolver()