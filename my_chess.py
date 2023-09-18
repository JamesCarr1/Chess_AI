import chess
import variables
import torch
import numpy as np

from numba import jit, njit, int32
from numba.experimental import jitclass

import numba.np.unsafe.ndarray

class stack():
    def __init__(self):
        self.values = []
    
    def push(self, item):
        """Adds the item to the top of the stack"""
        self.values.append(item)
    
    def pop(self):
        """Removes the item on top of the stack and returns it"""
        item = self.values.pop(-1)
        return item

class EmptyPiece(chess.Piece):
    def __init__(self):
        self.piece_type = 0
        self.color = 0

class TensorBoard(chess.Board):
    """
    Extension of chess.Board class that also has the capability of converting the current position to a tensor.
    """
    def __init__(self):
        super().__init__()
        self.as_array = np.array(variables.base_board)
        self.previous_positions = stack() # A stack object containing all previous positions in this tree

    def push(self, move: chess.Move) -> None:
        super().push(move)
        self.previous_positions.push(np.copy(self.as_array)) # Put current position on the stack
        self.update_array(move) # Now update current position

    def pop(self):
        super().pop()
        self.as_array = self.previous_positions.pop() # pop the previous position from the stack and update the as_array
    
    def update_array(self, move):
        # Update the array with the move
        self.as_array[move.to_square] = self.as_array[move.from_square]
        self.as_array[move.from_square] = 0

        # Check the other conditions
        self.as_array[64] = 1 - self.as_array[64] # Is now oter player's turn
        ### Format the castling rights
        for i, (colour, multiplier) in enumerate(variables.colours):
            self.as_array[65 + 2 * i] = self.has_kingside_castling_rights(colour)
            self.as_array[65 + 2 * i + 1] = self.has_queenside_castling_rights(colour)
        ### Format the en-passant
        self.as_array[69] = -1 if self.ep_square is None else self.ep_square
    
    """
    def as_tensor(self):
        '''
        Returns a flattened tensor representation of the board.

        returns:
            board_as_tensor: a 70 length vector. Indices 0-63 correspond to the current board position.
                             index 64 corresponds to the turn (i.e white=0, black=1)
                             index 65, 66, 67 and 68 indicate whether white and black can castle king and queenside respectively, 1 for true, 0 for false.
                             index 69 indicates if en-passant is legal and if so, which square. -1 indicates no en-passant possible 
        '''
        board_info = np.zeros(70)

        ### Format the board position
        for piece, colour, multiplier in variables.piece_types:
            for index in self.pieces(piece, colour):
                board_info[index] = piece * multiplier
    
        ### Format the turn
        board_info[64] = self.turn # need to multiply by 1 as it returns a bool

        ### Format the castling rights
        for i, (colour, multiplier) in enumerate(variables.colours):
            board_info[65 + 2 * i] = self.has_kingside_castling_rights(colour)
            board_info[65 + 2 * i + 1] = self.has_queenside_castling_rights(colour)
        
        ### Format en-passant
        # Board.ep_square just returns the index of the en-passant square
        board_info[69] = -1 if self.ep_square is None else self.ep_square

        return torch.tensor(board_info)
        """
    def as_tensor(self):
        return torch.tensor(self.as_array)