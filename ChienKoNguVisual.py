import random
import time
import pygame as p
from MinimaxVisualizer import MinimaxVisualizer

pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

knightScore =  [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

bishopScore =  [[4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]

queenScore =   [[1, 1, 1, 3, 1, 1, 1, 1],
                [1, 2, 3, 3, 3, 1, 1, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 2, 3, 3, 3, 1, 1, 1],
                [1, 1, 1, 3, 1, 1, 1, 1]]

rookScore =    [[4, 3, 4, 4, 4, 4, 3, 4],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [1, 1, 2, 3, 3, 2, 1, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 1, 2, 3, 3, 2, 1, 1],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [4, 3, 4, 4, 4, 4, 3, 4]]

whitePawnScore =   [[8, 8, 8, 8, 8, 8, 8, 8],
                    [8, 8, 8, 8, 8, 8, 8, 8],
                    [5, 6, 6, 7, 7, 6, 6, 5],
                    [2, 3, 3, 5, 5, 3, 3, 2],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [1, 2, 3, 3, 3, 3, 2, 1],
                    [1, 1, 1, 0, 0, 1, 1, 1],
                    [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScore =   [[0, 0, 0, 0, 0, 0, 0, 0],
                    [1, 1, 1, 0, 0, 1, 1, 1],
                    [1, 2, 3, 3, 3, 3, 2, 1],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [2, 3, 3, 5, 5, 3, 3, 2],
                    [5, 6, 6, 7, 7, 6, 6, 5],
                    [8, 8, 8, 8, 8, 8, 8, 8],
                    [8, 8, 8, 8, 8, 8, 8, 8]]

piecePosScores = {'N': knightScore, 'B': bishopScore, 'Q': queenScore, 'R': rookScore, "wp": whitePawnScore, "bp": blackPawnScore}

CHECKMATE = 1000
STALEMATE = 0
MAX_DEPTH = 3  # Reduced depth for better visualization

# Create visualizer instance
visualizer = MinimaxVisualizer(800, 600)
nextMove = None
nodes = 0

def findRandomMove(validMoves):
    if len(validMoves) > 0:
        return validMoves[random.randint(0, len(validMoves)-1)]

def findBestMoveMinimax(gs, validMoves):
    global nextMove
    global nodes
    nextMove = None
    alpha = -CHECKMATE
    beta = CHECKMATE
    nodes = 0
    
    # Limit moves for better visualization
    if len(validMoves) > 10:
        # Either take the first 10 or randomly sample
        validMoves = random.sample(validMoves, 10)
    
    start_time = time.time()
    findMoveMinimax(gs, validMoves, MAX_DEPTH, alpha, beta, gs.whiteToMove)
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
    print(f"Nodes searched: {nodes}")
    
    return nextMove

def findMoveMinimax(gs, validMoves, depth, alpha, beta, whiteToMove):
    global nextMove
    global nodes
    nodes += 1
    
    # Record this node evaluation in the visualization
    is_leaf = (depth == 0 or gs.checkMate or gs.staleMate)
    
    if is_leaf:
        score = scoreBoard(gs)
        visualizer.record_evaluation(None, score, MAX_DEPTH - depth, whiteToMove, 
                                   alpha, beta, is_leaf=True)
        return score
    
    # Limit branching factor for lower depths to keep visualization manageable
    if depth < 2 and len(validMoves) > 5:
        validMoves = validMoves[:5]
    
    random.shuffle(validMoves)
    
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinimax(gs, nextMoves, depth - 1, alpha, beta, False)
            gs.undoMove()
            
            # Record this node in the visualization
            pruned = beta <= alpha
            visualizer.record_evaluation(move, score, MAX_DEPTH - depth, 
                                       whiteToMove, alpha, beta, pruned=pruned)
            
            if score > maxScore:
                maxScore = score
                if depth == MAX_DEPTH:
                    nextMove = move
            alpha = max(alpha, score)
            if beta <= alpha:
                break
        return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinimax(gs, nextMoves, depth - 1, alpha, beta, True)
            gs.undoMove()
            
            # Record this node in the visualization
            pruned = beta <= alpha
            visualizer.record_evaluation(move, score, MAX_DEPTH - depth, 
                                       whiteToMove, alpha, beta, pruned=pruned)
            
            if score < minScore:
                minScore = score
                if depth == MAX_DEPTH:
                    nextMove = move
            beta = min(beta, score)
            if beta <= alpha:
                break
        return minScore

def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE  # Black wins
        else:
            return CHECKMATE   # White wins
    elif gs.staleMate:
        return STALEMATE
    
    score = 0
    for row in range(8):
        for col in range(8):
            square = gs.board[row][col]
            if square != "--":
                piecePosScore = 0
                if square[1] != "K":
                    if square[1] == "p":
                        piecePosScore = piecePosScores[square][row][col]
                    else:
                        piecePosScore = piecePosScores[square[1]][row][col]
                if square[0] == 'w':
                    score += pieceScore[square[1]] + piecePosScore * 0.1
                elif square[0] == 'b':
                    score -= pieceScore[square[1]] + piecePosScore * 0.1
    return score

def get_visualization_surface():
    """Return the current visualization surface"""
    return visualizer.draw()