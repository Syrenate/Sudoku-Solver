from .Board import Board

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