import pandas as pd
import os
import torch

import variables # Contains variables too unwieldy to store in this file

class ChessPosition():
    """
    Class containing the position pieces at some given point in the game.

    args:
        n: number of moves to position
        all_moves: all moves in the game
        result: [1-0], [0-1] or [1/2-1/2]
    
    attributes:
        self.n: same as n
        self.all_moves: same as all_moves
        self.position: position after n moves. See variables.py for definition of each value.
        self.label: [1-0]: 1, [1/2-1/2]: 0, [0-1]: -1. Could use tanh activation function on o/p layer
    """
    def __init__(self, n, all_moves, result):
        self.n = n
        self.all_moves = all_moves

        self.position = variables.initial_position

        self.label = variables.result_label_translation[result]


if __name__ == '__main__':
    raw_data_path = f"{os.getcwd()}/data/raw_data/chess_games.csv"
    raw_data = pd.read_csv(raw_data_path)
    event_types = raw_data['Event'].unique()
    print(event_types)