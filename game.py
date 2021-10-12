import pygame.freetype
from ai import *
from gamestate import *
import pygame as p
from zobrist import *

p.init()
WIDTH = HEIGHT = 660
DIMENSION = 11
SQ_SIZE = HEIGHT // DIMENSION
GAME_FONT = p.freetype.Font("Roboto-Black.ttf", 24)
MAX_FPS = 15
IMAGES = {}
MINMAX_DEPTH = 2
zobTable = [[[random.randint(1,2**64 - 1) for i in range(3)]for j in range(11)]for k in range(11)]
TT = {}

def loadImages():
    pieces = ["gE", "sE", "gF"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("C:/Users/Dogan/PycharmProjects/BT/New/images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def sidemenu(gamestate, screen):
    if gamestate.goldToMove:
        GAME_FONT.render_to(screen, (720, 70), "Gold's Turn", (255, 255, 255))
        if gamestate.firstMove:
            GAME_FONT.render_to(screen, (720, 130), "First Move", (255, 255, 255))
        else:
            GAME_FONT.render_to(screen, (710, 130), "Second Move", (255, 255, 255))

    elif not gamestate.goldToMove:
        GAME_FONT.render_to(screen, (710, 70), "Silver's Turn", (255, 255, 255))
        if gamestate.firstMove:
            GAME_FONT.render_to(screen, (720, 130), "First Move", (255, 255, 255))
        else:
            GAME_FONT.render_to(screen, (710, 130), "Second Move", (255, 255, 255))

def highlightSquares(screen, gs, validmoves, sqSelected, color):
    if sqSelected != ():
        r, c, = sqSelected
        if gs.board[r][c][0] == ('g' if gs.goldToMove else 's'):  # selected Square is a piece that can be moves
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency value -> 0 transparent 255 solid
            s.fill(p.Color('green'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # highliht moves from that square
            s.fill(color)
            for move in validmoves:
                if move.startRow == r and move.startCol == c:  # all the moves that belong to the pawn in r,c
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)  # draw squares on the board
    drawPieces(screen, gs.board)  # draw pieces on top of squares
    highlightSquares(screen, gs, validMoves, sqSelected, p.Color("yellow"))
    #highlightSquares(screen, gs, captureMoves, sqSelected, p.Color("red"))

def drawBoard(screen):


    for i in range(0,660+1,60):
        p.draw.line(screen,(255,255,255),(i,0),(i,660),1)
        p.draw.line(screen,(255,255,255),(0,i),(660,i),1)

    for j in range(180, 480+1, 60):
        p.draw.line(screen, (255, 255, 255), (j, 180-2), (j, 480+2), 5)
        p.draw.line(screen, (255, 255, 255), (180+2, j), (480+2, j), 5)

    p.draw.line(screen,(255,255,255),(660-2,0),(660-2,660),2)
    p.draw.line(screen,(255,255,255),(900-2,0),(900-2,660),2)
    p.draw.line(screen, (255,255,255), (0, 660 - 2), (900, 660 - 2), 2)
    #p.draw.line(screen, (255,255,255), (0, 660 - 2), (0, 660 - 2), 2)# fix for out of window line

    p.draw.line(screen, (255, 255, 255), (660, 540), (900, 540), 2)
    p.draw.line(screen, (255, 255, 255), (660, 420), (900, 420), 2)
    p.draw.line(screen, (255, 255, 255), (660, 300), (900, 300), 2)
    GAME_FONT.render_to(screen, (755, 470), "Undo", (255, 255, 255))
    GAME_FONT.render_to(screen, (770, 590), "AI", (255, 255, 255))
    GAME_FONT.render_to(screen, (740, 350), "Restart", (255, 255, 255))

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    pygame.display.set_caption('Breakthru')
    screen = p.display.set_mode((WIDTH + 240, HEIGHT))
    clock = p.time.Clock()
    gs = GameState()
    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []

    while running and not gs.isTerminal:
        if (gs.rowF == 10) or (gs.rowF == 0) or (gs.colF == 10) or (gs.colF == 10):
            gs.isTerminal = True

        elif gs.goldFlagship == 0:
            gs.isTerminal = True

        for e in p.event.get():
            validmoves = gs.getAllPossibleMoves()

            if e.type == p.QUIT:
                running=False

            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

                if col<12:
                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []

                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)

                    if len(playerClicks) == 2:
                        if row>10 or col>10:
                            sqSelected = ()
                            playerClicks = []
                        else:
                            move = Move(playerClicks[0], playerClicks[1], gs.board)

                        if len(validmoves) == 0:
                            if gs.isFirstMove:

                                gs.isStalemate = True
                                gs.isTerminal = True
                            else:
                                gs.goldToMove = not gs.goldToMove


                        elif move in validmoves:
                            gs.makeMove(move)
                            print(AI.evaluation(gs))

                            sqSelected = ()
                            playerClicks = []

                        else:
                            playerClicks = [sqSelected] # second click and avoid problem when i click black squares
                else:
                    if col>=11 and row>=9:
                        GAME_FONT.render_to(screen, (720, 200), "AI thinking..", (255, 255, 255))
                        p.display.flip()

                        value, move = AI.aspirationsearch(gs, 3, not gs.goldToMove)
                        #print(move.startRow, move.startCol)
                        #print(move.endRow, move.endCol)
                        gs.makeMove(move)
                        print(AI.evaluation(gs))


                    elif col>=11 and row>=7 and row<=9:
                        gs.undoMove()

                    elif col>=11 and row>=5 and row<=7:
                        main()

                    else:
                        sqSelected = ()
                        playerClicks = []



        screen.fill(p.Color("black"))
        drawGameState(screen, gs, validmoves, sqSelected)
        sidemenu(gs, screen)
        clock.tick(MAX_FPS)
        p.display.flip()

    while running:
        screen.fill(p.Color("black"))
        drawGameState(screen, gs, validmoves, sqSelected)



        if gs.isTerminal and AI.evaluation(gs)<0:
            GAME_FONT.render_to(screen, (720, 100), "Gold Player", (255, 255, 255))
            GAME_FONT.render_to(screen, (750, 120), "Wins!", (255, 255, 255))
        elif gs.isTerminal and AI.evaluation(gs)>0:
            GAME_FONT.render_to(screen, (720, 100), "Silver Player", (255, 255, 255))
            GAME_FONT.render_to(screen, (750, 120), "Wins!", (255, 255, 255))

        for e in p.event.get():

            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # get x,y location of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if col >= 11 and row >= 7 and row <= 9:
                    gs.undoMove()
                    gs.isTerminal = False
                elif col >= 11 and row >= 5 and row <= 7:
                    main()
        p.display.flip()


if __name__ == "__main__":
    main()
