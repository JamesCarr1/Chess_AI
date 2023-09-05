import pandas as pd
import os

if __name__ == '__main__':
    raw_data_path = f"{os.getcwd()}/data/raw_data/chess_games.csv"
    raw_data = pd.read_csv(raw_data_path)
    event_types = raw_data['Event'].unique()
    print(event_types)