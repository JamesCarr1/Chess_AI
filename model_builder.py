import torch
import random

import variables

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

    current_position = torch.tensor([-4, -2, -3, -5, -6, -3, -2, -4, -1, -1, -1, -1, -1, -1,
                        -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 
                        1, 1, 1, 1, 1, 4, 2, 3, 5, 6, 3, 2, 4, 0, 1, 1, 1, 1, 20])
    
    without_one_black_knight = torch.tensor([-4, 0, -3, -5, -6, -3, -2, -4, -1, -1, -1, -1, -1, -1,
                        -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 
                        1, 1, 1, 1, 1, 4, 2, 3, 5, 6, 3, 2, 4, 0, 1, 1, 1, 1, 20])
    
    base(current_position)
    base(without_one_black_knight)
