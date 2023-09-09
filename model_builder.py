import torch
import random

import variables
import data_generator

class BaseModel(torch.nn.Module):
    """
    Base model which counts the total material on the board and returns it as an evaluation.
    """
    def __init__(self, material_values):
        super().__init__()
        self.material_values = material_values

    def forward(self, board):
        # Take the first 64 elements (i.e the board layout) and convert each piece to it's material value. 
        # Have to convert to string before tensor else torch cannot infer dtype
        evaluation = torch.tensor(list(map(lambda piece: self.material_values[piece.item()], board[0:64])))

        # And sum all elements in the tensor
        evaluation = torch.sum(evaluation)
        
        return evaluation.item()

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
