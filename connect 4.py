#!/usr/bin/env python3

import os
import numpy as np
import pygame
import sys
import math
import random
import time

# Ensure pygame is properly initialized
try:
    pygame.init()
except pygame.error as e:
    print(f"Failed to initialize pygame: {e}")
    sys.exit(1)

# Constants
ROW_COUNT = 6
COLUMN_COUNT = 7
PLAYER = 0
AI = 1
PLAYER_PIECE = 1
AI_PIECE = 2
WINDOW_LENGTH = 4

# Colors
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
PINK = (255, 105, 180)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Pygame setup
SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE / 2 - 5)

screen = pygame.display.set_mode(size)
myfont = pygame.font.SysFont("monospace", 75)
clock = pygame.time.Clock()

def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT), int)

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    # Return True if there is any empty spot in the column
    return board[0][col] == 0  # We check the top row (row 0), ensuring the column has space.

def get_next_open_row(board, col):
    # Find the next available empty row in the column (starts from the bottom)
    for r in range(ROW_COUNT - 1, -1, -1):  # Start from the bottom row
        if board[r][col] == 0:
            return r  # Return the first empty row found from the bottom upwards.
    return None  # If no empty rows are found (column is full), return None

def winning_move(board, piece):
    # Horizontal
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if all(board[r][c + i] == piece for i in range(WINDOW_LENGTH)):
                return [(r, c + i) for i in range(WINDOW_LENGTH)]
    # Vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c] == piece for i in range(WINDOW_LENGTH)):
                return [(r + i, c) for i in range(WINDOW_LENGTH)]
    # Positive Diagonal
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c + i] == piece for i in range(WINDOW_LENGTH)):
                return [(r + i, c + i) for i in range(WINDOW_LENGTH)]
    # Negative Diagonal
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if all(board[r - i][c + i] == piece for i in range(WINDOW_LENGTH)):
                return [(r - i, c + i) for i in range(WINDOW_LENGTH)]
    return None

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2
    if window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 4
    return score

def score_position(board, piece):
    score = 0
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    score += center_array.count(piece) * 3
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)
    for r in range(3, ROW_COUNT):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)
    return score

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    terminal = is_terminal_node(board)
    if depth == 0 or terminal:
        if terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -100000000)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value
    else:
        value = math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value

def get_valid_locations(board):
    return [c for c in range(COLUMN_COUNT) if is_valid_location(board, c)]

def draw_board(board, highlight=[]):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, (r+1)*SQUARESIZE, SQUARESIZE, SQUARESIZE))
            # Corrected row position
            color = WHITE if board[r][c] == 0 else (CYAN if board[r][c] == PLAYER_PIECE else PINK)
            y = (r + 1) * SQUARESIZE + SQUARESIZE // 2
            if (r, c) in highlight:
                pygame.draw.circle(screen, YELLOW, (c*SQUARESIZE + SQUARESIZE//2, y), RADIUS + 5)
            pygame.draw.circle(screen, color, (c*SQUARESIZE + SQUARESIZE//2, y), RADIUS)
    pygame.display.update()

def animate_drop(board, col, row, piece):
    for r in range(row + 1):
        temp_board = board.copy()
        temp_board[r][col] = piece
        color = CYAN if piece == PLAYER_PIECE else PINK
        pygame.draw.rect(screen, BLUE, (0, 0, width, height))  # Redraw background
        draw_board(temp_board)
        pygame.display.update()
        pygame.time.wait(50)

# Game Loop
board = create_board()
game_over = False
turn = random.choice([PLAYER, AI])
draw_board(board)

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEMOTION and not game_over:  # Ensure game is not over
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            posx = event.pos[0]
            color = CYAN if turn == PLAYER else PINK
            pygame.draw.circle(screen, color, (posx, SQUARESIZE // 2), RADIUS)
            pygame.display.update()
        if event.type == pygame.MOUSEBUTTONDOWN and turn == PLAYER and not game_over:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            posx = event.pos[0]
            col = posx // SQUARESIZE
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                animate_drop(board, col, row, PLAYER_PIECE)
                drop_piece(board, row, col, PLAYER_PIECE)
                win_seq = winning_move(board, PLAYER_PIECE)
                if win_seq:
                    draw_board(board, win_seq)
                    label = myfont.render("Player Wins!", True, CYAN)
                    screen.blit(label, (40, 10))
                    game_over = True
                else:  # Only switch turn if no winner
                    turn = AI
                draw_board(board)

    if turn == AI and not game_over:
        pygame.time.wait(500)
        col, _ = minimax(board, 5, -math.inf, math.inf, True)
        if col is not None and is_valid_location(board, col):  # Ensure valid AI move
            row = get_next_open_row(board, col)
            animate_drop(board, col, row, AI_PIECE)
            drop_piece(board, row, col, AI_PIECE)
            win_seq = winning_move(board, AI_PIECE)
            if win_seq:
                draw_board(board, win_seq)
                label = myfont.render("AI Wins!", True, PINK)
                screen.blit(label, (40, 10))
                game_over = True
            else:  # Only switch turn if no winner
                turn = PLAYER
            draw_board(board)

    if game_over:
        pygame.display.update()
        pygame.time.wait(3000)
