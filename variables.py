import torch

# White:            Black       
# - Pawn: 1         - Pawn: -1
# - Knight: 2       - Knight: -2
# - Bishop: 3       - Bishop: -3
# - Rook: 4         - Rook: -4
# - Queen: 5        - Queen: -5
# - King: 6         - King: -6

result_label_translation = {'[1-0]': 1,
                            '[0-1]': -1,
                            '[1/2-1/2]': 0}

# Translates a FEN piece code to my integer representation
fen_number_translation = {'P': 1,
                          'p': -1,
                          'N': 2,
                          'n': -2,
                          'B': 3,
                          'b': -3,
                          'R': 4,
                          'r': -4,
                          'Q': 5,
                          'q': -5,
                          'K': 6,
                          'k': -6}

# Translates a file letter (e.g e) to a number (e.g 5)
file_to_number = {'a': 1,
                  'b': 2,
                  'c': 3,
                  'd': 4,
                  'e': 5,
                  'f': 6,
                  'g': 7,
                  'h': 8}