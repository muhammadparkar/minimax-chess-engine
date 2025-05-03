import pygame as p
import ChessEngine
import ChienKoNguVisual

WIDTH = HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
VISUALIZATION_WIDTH = 800
VISUALIZATION_HEIGHT = 600
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}

def load_images():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        try:
            IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        except:
            print(f"Error loading image for {piece}")

def main():
    p.init()
    # Create a window to accommodate both game and visualization
    total_width = WIDTH + MOVE_LOG_PANEL_WIDTH + VISUALIZATION_WIDTH
    total_height = max(HEIGHT, VISUALIZATION_HEIGHT)
    screen = p.display.set_mode((total_width, total_height))
    p.display.set_caption("Chess Engine with Minimax Visualization")
    
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    gameOver = False
    playerOne = True   # Human plays white
    playerTwo = False  # AI plays black
    load_images()
    sqSelected = ()
    playerClicks = []
    show_visualization = True

    running = True
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    # Only process clicks on the chess board
                    if location[0] < WIDTH:
                        col = location[0]//SQ_SIZE
                        row = location[1]//SQ_SIZE
                        
                        # Same position clicked twice
                        if sqSelected == (row, col) or col >= 8:
                            sqSelected = ()
                            playerClicks = []
                        else:
                            sqSelected = (row, col)
                            playerClicks.append(sqSelected)
                            
                        # After second click
                        if len(playerClicks) == 2:
                            move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                            for valid_move in validMoves:
                                if move.moveID == valid_move.moveID:
                                    gs.makeMove(valid_move)
                                    moveMade = True
                                    animate = True
                                    sqSelected = ()
                                    playerClicks = []
                                    break
                            else:
                                playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    playerOne = True
                    playerTwo = True
                elif e.key == p.K_r:  # Reset
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    moveMade = False
                    animate = False
                    gameOver = False
                    playerOne = True
                    playerTwo = True
                    sqSelected = ()
                    playerClicks = []
                elif e.key == p.K_q:  # AI plays white
                    playerOne = False
                    playerTwo = True
                elif e.key == p.K_e:  # AI plays black
                    playerOne = True
                    playerTwo = False
                elif e.key == p.K_v:  # Toggle visualization
                    show_visualization = not show_visualization

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        # AI move finder
        if not gameOver and not humanTurn:
            AIMove = ChienKoNguVisual.findBestMoveMinimax(gs, validMoves)
            if AIMove is None:
                AIMove = ChienKoNguVisual.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        # Draw everything
        screen.fill(p.Color(50, 50, 50))
        
        # Draw chess game
        drawGameState(screen, gs, validMoves, sqSelected)
        
        # Draw visualization panel
        if show_visualization:
            visualization_surface = ChienKoNguVisual.get_visualization_surface()
            screen.blit(visualization_surface, (WIDTH + MOVE_LOG_PANEL_WIDTH, 0))
            
            # Draw divider line
            p.draw.line(screen, p.Color("black"), 
                       (WIDTH + MOVE_LOG_PANEL_WIDTH, 0), 
                       (WIDTH + MOVE_LOG_PANEL_WIDTH, total_height), 3)

        # Display end game text if needed
        if gs.checkMate or gs.staleMate:
            gameOver = True
            if gs.staleMate:
                drawEndGameText(screen, "DRAW")
            else:
                if gs.whiteToMove:
                    drawEndGameText(screen, "BLACK WINS")
                else:
                    drawEndGameText(screen, "WHITE WINS")

        clock.tick(MAX_FPS)
        p.display.flip()

def highlightMove(screen, gs, validMoves, sqSelected):
    sq = p.Surface((SQ_SIZE, SQ_SIZE))
    sq.set_alpha(100)
    if sqSelected != ():
        r, c = sqSelected
        if 0 <= r < 8 and 0 <= c < 8:  # Make sure it's within board bounds
            if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): 
                # Highlight selected square
                sq.fill(p.Color("blue"))
                screen.blit(sq, (c * SQ_SIZE, r * SQ_SIZE))
                # Highlight valid moves
                sq.fill(p.Color("cyan"))
                for move in validMoves:
                    if move.startRow == r and move.startCol == c:
                        screen.blit(sq, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))
    
    # Highlight check
    try:
        if hasattr(gs, 'inCheck') and gs.inCheck:
            if gs.whiteToMove:
                sq.fill(p.Color("red"))
                screen.blit(sq, (gs.whiteKingLocate[1] * SQ_SIZE, gs.whiteKingLocate[0] * SQ_SIZE))
            else:
                sq.fill(p.Color("red"))
                screen.blit(sq, (gs.blackKingLocate[1] * SQ_SIZE, gs.blackKingLocate[0] * SQ_SIZE))
    except:
        pass  # If attribute doesn't exist
    
    # Highlight last move
    if len(gs.moveLog) > 0:
        sq.fill(p.Color("yellow"))
        screen.blit(sq, (gs.moveLog[-1].startCol * SQ_SIZE, gs.moveLog[-1].startRow * SQ_SIZE))
        screen.blit(sq, (gs.moveLog[-1].endCol * SQ_SIZE, gs.moveLog[-1].endRow * SQ_SIZE))

def animateMove(move, screen, board, clock):
    colors = [p.Color("white"), p.Color("grey")]
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5
    frameCount = max(abs(dR), abs(dC)) * framesPerSquare
    
    if frameCount == 0:  # Avoid division by zero
        frameCount = 1
        
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        
        # Erase the moving piece from its starting square
        color = colors[(move.startRow + move.startCol) % 2]
        startSquare = p.Rect(move.startCol*SQ_SIZE, move.startRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, startSquare)
        
        # Draw captured piece in the end square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        
        # Draw moving piece
        if move.pieceMoved != "--":
            if move.pieceMoved in IMAGES:
                screen.blit(IMAGES[move.pieceMoved], p.Rect(int(c*SQ_SIZE), int(r*SQ_SIZE), SQ_SIZE, SQ_SIZE))
        
        p.display.flip()
        clock.tick(60)

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightMove(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs)

def drawBoard(screen):
    colors = [p.Color("white"), p.Color("grey")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--" and piece in IMAGES:
                screen.blit(IMAGES[piece], p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawEndGameText(screen, text):
    font = p.font.SysFont("Verdana", 32, True, False)
    textObject = font.render(text, False, p.Color("black"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, False, p.Color("red"))
    screen.blit(textObject, textLocation.move(2, 2))

def drawMoveLog(screen, gs):
    moveLogRect = p.Rect(WIDTH, 0, MOVE_LOG_PANEL_WIDTH, HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i+1 < len(moveLog):
            moveString += str(moveLog[i+1]) + "   "
        moveTexts.append(moveString)
    
    padding = 5
    movesPerRow = 1
    lineSpacing = 2
    textY = padding
    
    font = p.font.SysFont("Verdana", 13, True, False)
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i+j < len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text, False, p.Color("white"))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing

if __name__ == "__main__":
    main()