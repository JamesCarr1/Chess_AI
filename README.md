Data is available at: https://www.kaggle.com/datasets/arevel/chess-games. Place in data/raw_data folder

# Repo Structure

Chess_AI/
|---data_setup.py
|---engine.py
|---model_builder.py
|---train.py
|---utils.py
|---models/
|
|---data/
    |---raw_data/
    |   |---chess_games.csv
    |---train/
    |   |---1-0/
    |   |   |---game01.pt
    |   |   |---...
    |   |---0-0/
    |   |   |---game03.pt
    |   |   |---...
    |   |---0-1/
    |       |---game05.pt
    |       |---...
    |---test/
    |   |---1-0/
    |   |   |---game07.pt
    |   |   |---...
    |   |---0-0/
    |   |   |---game08.pt
    |   |   |---...
    |   |---0-1/
    |       |---game09.pt
    |       |---...

# File Descriptions

## **data_setup.py**

- Takes data from chess_games.csv and creates usable data (into data/train and data/test).
- Creates Dataset to store games.
- Creates DataLoader to load games from dataset.

## **engine.py**

- Contains functions for training and testing model

## **model_builder.py**

- Contains model classes

## **train.py**

- Trains, evaluates and saves models

## **utils.py**

- Contains various other functions useful for the model