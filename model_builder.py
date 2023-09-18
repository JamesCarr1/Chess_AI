import torch
import random

import numpy as np

import variables
import data_generator

from numba import njit

class BaseModel(torch.nn.Module):
    """
    Base model which counts the total material on the board and returns it as an evaluation.
    """
    def __init__(self, material_values):
        super().__init__()
        self.material_values = material_values

    def forward(self, board):
        # Take the first 64 elements (i.e the board layout) and convert each piece to it's material value.

        # Alterative, slightly slower method
        #evaluation = [self.material_values[piece.item()] for piece in board[0:64]]
        #evaluation = sum(evaluation)

        return base_model_forward(np.array(board[0:64]))

    def calc_piece_value(self, piece):
        return self.material_values[piece.item()]

@njit
def base_model_forward(board: np.array):
    """
    forward() function of base_model that can be jit compiled with Numba
    """
    evaluation = 0
    for piece in board:
        # Calculate colour
        if piece >= 0:
            colour_multiplier = 1
        else:
            colour_multiplier = -1
        
        if piece == 0:
            evaluation += 0
        elif abs(piece) == 1: # i.e a pawn
            evaluation += 1 * colour_multiplier
        elif abs(piece) == 2 or 3: # i.e a knight or bishop
            evaluation += 3 * colour_multiplier
        elif abs(piece) == 4: # i.e a rook
            evaluation += 5 * colour_multiplier
        elif abs(piece) == 5: # i.e a queen
            evalutation += 9 * colour_multiplier

    return evaluation

class RandomModel(torch.nn.Module):
    """
    Test model to test if a game can actually be played.
    """
    def __init__(self):
        super().__init__()

    def forward(self, path):
        # Just randomly chooses a move
        return random.randint(0, 100)

if __name__ == '__main__':
    base = BaseModel(variables.material_values)

    test_fen = 'r2q1b1r/ppp1kppp/2np1n2/4p3/Q1P3P1/5N2/PP1PPPP1/RNB1KB1R w KQ - 1 7'
    test_board = data_generator.TensorBoard()
    test_board.set_fen(test_fen)

    print(base(test_board.as_tensor()))
