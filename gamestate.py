from move import *

class GameState():
    def __init__(self):
        # 2-D array representation of the board
        self.board = [
            ["--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "sE", "sE", "sE", "sE", "sE", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "sE", "--", "--", "gE", "gE", "gE", "--", "--", "sE", "--"],
            ["--", "sE", "--", "gE", "--", "--", "--", "gE", "--", "sE", "--"],
            ["--", "sE", "--", "gE", "--", "gF", "--", "gE", "--", "sE", "--"],
            ["--", "sE", "--", "gE", "--", "--", "--", "gE", "--", "sE", "--"],
            ["--", "sE", "--", "--", "gE", "gE", "gE", "--", "--", "sE", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "sE", "sE", "sE", "sE", "sE", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--", "--", "--", "--"]
        ]

        # Indicates which player's turn it is
        self.goldToMove = True

        #Coordinates of the flagship
        self.rowF = 5
        self.colF = 5

        # MoveLog and capturelog as lists, appended each time a piece moves or is captured
        self.moveLog = []
        self.pieceCaptured = []

        # Due to two move possibility, this attribute indicates whether the first move is made (true if not made)
        self.firstMove = True

        # Indicates if it is game over
        self.isTerminal = False

        # Special case for draws
        self.isStalemate = False

        # Some helper attributes for the getAllPossibleMoves function
        self.oldMoveRow = None
        self.oldMoveCol = None
        self.oldPiece = None

        #Number of pieces in the board, used in evaluation function
        self.silverEscort = 20
        self.goldEscort = 12
        self.goldFlagship = 1
        self.turn_counter = 0


    # Function that physically changes the board when a move is made
    def makeMove(self, move):

        self.board[move.startRow][move.startCol] = "--"
        if self.firstMove == False:
            self.board[move.endRow][move.endCol] = move.pieceMoved
            self.moveLog.append(move)
            self.goldToMove = not self.goldToMove
            self.firstMove = True
            self.oldMoveRow = None
            self.oldMoveCol = None
            self.oldPiece = None

        else:
            if self.board[move.endRow][move.endCol] != "--":
                self.pieceCaptured.append(self.board[move.endRow][move.endCol])
                if self.pieceCaptured[-1] == 'gF':
                    self.goldFlagship -= 1
                    self.isTerminal = True

                elif self.pieceCaptured[-1][0] == 's':
                    self.silverEscort -= 1

                elif self.pieceCaptured[-1] == 'gE':
                    self.goldEscort -= 1

                elif move.pieceMoved == 'gF':
                    self.silverEscort -= 1
                    self.rowF = move.endRow
                    self.colF = move.endCol
                    if (move.endCol == 10) or (move.endCol == 0) or (move.endRow == 0) or (move.endRow == 10):
                        self.isTerminal = True

                self.goldToMove = not self.goldToMove

            else:
                self.oldMoveRow = move.endRow
                self.oldMoveCol = move.endCol

                if move.pieceMoved == 'gF':
                    self.goldToMove = not self.goldToMove
                    self.rowF = move.endRow
                    self.colF = move.endCol

                    if (move.endCol == 10) or (move.endCol == 0) or (move.endRow == 0) or (move.endRow == 10):
                        self.isTerminal = True

                else:
                    self.firstMove = False

                self.oldPiece = move.pieceMoved

            self.board[move.endRow][move.endCol] = move.pieceMoved
            self.moveLog.append(move)


    # Undo move function
    def undoMove(self):
        turn = self.goldToMove
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            if self.firstMove == False:
                self.firstMove = True
                pass
            elif move.pieceCaptured != '--':
                self.goldToMove = not self.goldToMove

                if move.pieceCaptured == 'gF':
                    self.isTerminal = False
                    self.goldFlagship +=1
                elif move.pieceCaptured == 'gE':
                    self.goldEscort +=1
                else:
                    self.silverEscort += 1

            else:
                if not self.firstMove:
                    self.firstMove = True
                else:
                    self.goldToMove = not self.goldToMove
                    self.firstMove = False

                if move.pieceMoved[1] == 'F':
                    self.goldToMove = not self.goldToMove
                    if self.isTerminal:
                        self.isTerminal=False

    # The function calculates the possible moves for each individual piece on the board
    def getMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        for d in directions:
            for i in range(1, 10):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 10 and 0 <= endCol <= 10:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    else:
                        break
                else:
                    break

    # The function calculates the possible captures for each individual piece on the board
    def getCaptureMoves(self, r, c, capture):
        enemy = 's' if self.goldToMove else 'g'
        # possible captures
        if self.firstMove:
            for i in range(0, 2):
                newCol = c - 1 if i == 0 else c + 1
                if 0 <= newCol <= 10:
                    if r - 1 >= 0:
                        if self.board[r - 1][newCol][0] == enemy:
                            capture.append(Move((r, c), (r - 1, newCol), self.board))
                    if r + 1 <= 10:
                        if self.board[r + 1][newCol][0] == enemy:
                            capture.append(Move((r, c), (r + 1, newCol), self.board))

    # Move generator function that returns a list of possible moves with the self.isfirstMove and player color taken into consideration
    def getAllPossibleMoves(self):
        moves = []
        captures = []

        if self.goldToMove and not self.firstMove:
            for row in range(11):
                for col in range(11):
                    piece = self.board[row][col]
                    if piece == 'gE':
                        if self.oldMoveRow == row and self.oldMoveCol == col:
                            pass
                        else:
                            self.getMoves(row, col, moves)

        elif self.goldToMove and self.firstMove:

            for row in range(11):
                for col in range(11):
                    piece = self.board[row][col]
                    if piece == 'gF' or piece == 'gE':
                        self.getMoves(row, col, moves)
                        self.getCaptureMoves(row, col, captures)

        elif not self.goldToMove and not self.firstMove:
            for row in range(11):
                for col in range(11):
                    piece = self.board[row][col]
                    if piece == 'sE':
                        if self.oldMoveRow != row or self.oldMoveCol != col:
                            self.getMoves(row, col, moves)

        else:
            for row in range(11):
                for col in range(11):
                    piece = self.board[row][col]
                    if piece == 'sE':
                        self.getMoves(row, col, moves)
                        self.getCaptureMoves(row, col, captures)

        return captures + moves #Some trivial move-ordering, checks the capture moves first


    # Helper functions for board evaluation
    def getCaptureMovesF(self, r, c, capture):
        enemy = 's'
        # possible captures
        if self.firstMove:
            for i in range(0, 2):
                newCol = c - 1 if i == 0 else c + 1
                if 0 <= newCol <= 10:
                    if r - 1 >= 0:
                        if self.board[r - 1][newCol][0] == enemy:
                            capture.append(Move((r, c), (r - 1, newCol), self.board))
                    if r + 1 <= 10:
                        if self.board[r + 1][newCol][0] == enemy:
                            capture.append(Move((r, c), (r + 1, newCol), self.board))
    def getMovesF(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        for d in directions:
            for i in range(1, 10):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 10 and 0 <= endCol <= 10:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    else:
                        break
                else:
                    break

