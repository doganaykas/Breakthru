import random

# Initializing random values for the board
zobTable = [[[random.randint(1,2**64 - 1) for i in range(3)]for j in range(11)]for k in range(11)]

def indexing(piece):
    ''' mapping each piece to a particular number'''
    if (piece=='gF'):
        return 0
    if (piece=='gE'):
        return 1
    if (piece=='sE'):
        return 2
    else:
        return -1


def computeHash(board):
    h = 0
    for i in range(11):
        for j in range(11):
            if board[i][j] != '--':
                piece = indexing(board[i][j])
                h ^= zobTable[i][j][piece]
    return h

