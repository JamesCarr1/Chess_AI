import chess

class MoveTree():
    """A tree containing all possible moves up to a certain depth"""
    def __init__(self, move):
        self.move = move
        self.nodes = []

    def add_node(self, move):
        self.nodes.append(MoveTree(move))
    
    def __repr__(self):
        return f"MoveTree({self.move}): {self.nodes}"
    
    def is_leaf(self):
        # If nodes list is empty, return true.
        # bool of an empty list == false, so return not bool(list)
        return not bool(self.nodes)

# Generates games given two models

def generate_games(model, base_model, depth, batch_size):
    """
    Takes in two models and plays a number of games against each other, returning the moves of each game.
    
    args:
        model: the model to be trained
        base_model: the model trained against
        depth: how far the model searches to evaluate positions
        batch_size: number of games played
    returns:
        games: a list of movetext files, including all info from the game.
    """

def play_game(model, base_model, depth):
    """
    Plays a game between the two models.

    args:
        model_w: controls white
        model_b: controls black
        depth: how far the model searches to evaluate positions
    returns:
        game_moves: a movetext including all moves
    """
    game = chess.Board()

    # Whilst the game is still going
    while game.outcome() is None:
        # Generate all possible legal moves
        depth_1_moves = game.legal_moves
        print(list(depth_1_moves))
        break

if __name__ == '__main__':
    #play_game(1, 1, 1)

    game = chess.Board()
    moves_tree = MoveTree('Start')
    for move in list(game.legal_moves):
        moves_tree.add_node(move)
    
    for i, node in enumerate(moves_tree.nodes):
        # Move game forward by step
        game.push(node.move)
        # Calculate all legal moves and append to tree
        for new_move in list(game.legal_moves):
            moves_tree.nodes[i].add_node(new_move)
        # Return back to original position
        game.pop()
    
    print(moves_tree.nodes[0])