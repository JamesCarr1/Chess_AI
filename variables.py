import torch

# White:            Black:
# - King: 1         - King: -1         
# - Pawn: 2         - Pawn: -2
# - Knight: 3       - Knight: -3
# - Bishop: 4       - Bishop: -4
# - Rook: 5         - Rook: -5
# - Queen: 6        - Queen: -6

# Note: first row in tensor is equivalent to 1 rank on board. Eighth row in tensor is equivalent to 8 rank
initial_position = torch.tensor([[5 , 3 , 4 , 1 , 6 , 4 , 3 , 5 ], # rank 1
                                 [2 , 2 , 2 , 2 , 2 , 2 , 2 , 2 ],
                                 [0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ],
                                 [0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ],
                                 [0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ],
                                 [0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ],
                                 [-2, -2, -2, -2, -2, -2, -2, -2],
                                 [-5, -3, -4, -1, -6, -4, -3, -5]])  # rank 8

result_label_translation = {'[1-0]': 1,
                            '[0-1]': -1,
                            '[1/2-1/2]': 0}