import torch
import pandas as pd
import numpy as np
import os

from pathlib import Path

def trim_dataset(data_path):
    """
    Opens the csv file in 'datapath', removes irrelevant columns and saves as a new csv
    """
    save_folder = Path(os.getcwd()) / 'data'

    # Check the save path exists, if not, make it
    if not os.path.isdir(save_folder):
        os.mkdir(save_folder)

    save_path = save_folder / 'trimmed_game_data.csv'

    # Open up the data
    full_data = pd.read_csv(data_path)

    # Extract relevant columns
    columns_to_keep = ['Event', 'Result', 'AN', 'WhiteElo', 'BlackElo'] # The gamemode, winner and moves in the game, plus the elo of the players
    trimmed_data = full_data[columns_to_keep]

    # And save
    trimmed_data.to_csv(save_path)
    
def convert_str_result_to_multiclass(self, result):
    """
    Converts a result in string format (e.g "1-0") into a multiclass form:
        1-0     ->  [1, 0, 0]
        1/2-1/2 ->  [0, 1, 0]
        0-1     ->  [0, 0, 1]
    
        args:
            result: the game result in string format
    """
    if result == '1-0':
        return [1, 0, 0]
    elif result == '1/2-1/2':
        return [0, 1, 0]
    elif result == '0-1':
        return [0, 0, 1]
    else:
        return float('NaN') # If neither, return Nan
    
class ChessDB():
    """
    Contains a pandas dataframe that has some added functionality specifically for the chess database.

    args:
        mode: 'trim' or 'open'
    """
    def __init__(self, mode, data_path):
        # If in trim mode, open and 
        if mode == 'trim':
            self.data = self.open_and_format(data_path)
        elif mode == 'open':
            self.data = pd.read_csv(data_path)

    def open_and_format(self, data_path):
        """
        Opens the csv file in 'datapath', removes irrelevant columns, adjusts columns and saves as a new csv
        """
        save_folder = Path(os.getcwd()) / 'data'

        # Check the save path exists, if not, make it
        if not os.path.isdir(save_folder):
            os.mkdir(save_folder)

        save_path = save_folder / 'trimmed_game_data.csv'

        # Open up the data
        data = pd.read_csv(data_path)

        # Extract relevant columns
        columns_to_keep = ['Event', 'Result', 'AN', 'WhiteElo', 'BlackElo'] # The gamemode, winner and moves in the game, plus the elo of the players
        data = data[columns_to_keep]

        # Now format columns
        data['Result'] = self.format_results_column(data['Result'].to_numpy())
        data = data[~self.find_evals_mask(data['AN'])] # Finds a mask of all rows with stockfish evals, and removes them
        data['AN'] = list(map(self.convert_movetext_to_list, data['AN'].to_numpy()))
        
        # And save
        data.to_csv(save_path)

        return data

    def format_results_column(self, results):
        # Converts all string type results to a multiclass vector representation
        return list(map(self.convert_str_result_to_multiclass, results))

    def convert_str_result_to_multiclass(self, result):
        """
        Converts a result in string format (e.g "1-0") into a multiclass form:
            1-0     ->  [1, 0, 0]
            1/2-1/2 ->  [0, 1, 0]
            0-1     ->  [0, 0, 1]
        
            args:
                result: the game result in string format
        """
        if result == '1-0':
            return [1, 0, 0]
        elif result == '1/2-1/2':
            return [0, 1, 0]
        elif result == '0-1':
            return [0, 0, 1]
        else:
            return float('NaN') # If neither, return Nan
    
    def find_evals_mask(self, ANs):
        """
        Finds all rows with stockfish evaluations

        args:
            ANs: pd.Series object
        """
        mask = ANs.str.contains('{') # All evals start with this

        return mask

    def convert_movetext_to_list(self, moves):
        """
        Takes in a movetext string and converts it to a list of tuples
        """
        # Split into individual elements
        moves = moves.split(' ')[:-1] # last element is the result, which we already know
        # Remove the first of every three elements (i.e the '1.' in ['1.', 'e4', 'e5'])
        del moves[::3]
        # Now pair up elements. [::2] cycles through every OTHER element. 'None' ensures the last move is recorded if white won on the
        # last move. If black won, the 'None' part has no effect.
        moves = [(w_move, b_move) for w_move, b_move in zip(moves[::2], moves[1::2] + ['None'])]

        return moves

if __name__ == '__main__':
    # Uncomment if data has not yet been trimmed
    #format_dataset(Path(os.getcwd()) / 'data' / '...')