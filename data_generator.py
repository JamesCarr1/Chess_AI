import chess
import torch
import random

class MoveTree():
    """A tree containing all possible moves up to a certain depth
    
    attr:
        move: the current move at this node of the tree
        next_moves: all possible moves that can follow move
        parent: the move preceding move. Allows for bi-directional traversal (useful for retrieving the path).
    """
    def __init__(self, move, parent=None):
        self.move = move
        self.next_moves = []
        self.parent = parent

    def add_node(self, move):
        self.next_moves.append(MoveTree(move, parent=self))
    
    def __repr__(self):
        return f"MoveTree({self.move}): {self.next_moves}"
    
    def is_leaf(self):
        # If nodes list is empty, return true.
        # bool of an empty list == false, so return not bool(list)
        return not bool(self.next_moves)
    
    def get_path(self):
        """
        Returns the path of moves up to this move
        """
        path = [self.move] # initialise list with last (current) move
        parent = self.parent # get parent move
        while parent is not None:
            path.insert(0, parent.move) # insert previous move at front of list
            parent = parent.parent # update the parent
        return path

class ChessGame():
    """
    Contains the information for a single chess game, including the function to search for moves up to a certain depth.

    attr:
        current_position: A chess.Board instance that contains the current position of the game. Is also used to find all possible moves
        moves_tree: A MoveTree() instance that contains all of the possible moves up to a certain depth.
    """
    def __init__(self):
        self.current_position = chess.Board() # initialise with default position
        self.moves_tree = MoveTree('Start') # Just a placeholder

    def find_possible_moves(self, depth, tree):
        """
        Finds all moves up to a given depth. Returns the tree object.
        """

        if depth > 0:
            # Find all the legal moves at this level and append to nodes
            for move in list(self.current_position.legal_moves):
                tree.add_node(move)
            # Now progress to next level and cycle through each node at the current level and find new nodes a level deeper
            for new_tree in tree.next_moves:
                self.current_position.push(new_tree.move) # progress to next move
                if self.current_position.outcome() is None: # If game is over, don't try to find any more moves
                    self.find_possible_moves(depth - 0.5, new_tree) # find valid moves. One move is 'half a depth' so subtract 0.5
                self.current_position.pop() # move back to original position
        
        return tree

    def update_moves_tree(self, depth):
        self.moves_tree = self.find_possible_moves(depth=depth, tree=MoveTree('Start'))

    def get_all_paths(self, tree):
        """Searches each element of the tree and finds if it is a leaf. If it is, add path to list"""
        all_paths = []
        # First, check if next_moves is empty, if so, ignore it (already a leaf)
        if tree.is_leaf():
            return [tree.get_path()]
        
        # Now cycle through each child tree of tree
        for child_tree in tree.next_moves:
            # If the child is a leaf, add it's path
            if child_tree.is_leaf():
                all_paths.append(child_tree.get_path())
            # If the child is not a leaf, now search through the child tree
            else:
                # get_all_paths returns a list, but can also return a single value in a list
                # Even if it is just one pair, use a for loop to unpack
                for pair in self.get_all_paths(child_tree):
                    all_paths.append(pair)
        
        return all_paths

    def get_best_evals(self, tree, model, colour, max_min=[max, min]):
        """Searches each element of the tree and finds if it is a leaf. If it is, calculate it's evaluation and compare to others at the same depth.
        Repeat until the best evaluation is returned.

        args:
            tree: the current MoveTree object
            model: the model used to evaluate the moves
            colour: 0 for max (i.e black's turn), 1 for min (i.e white's turn).
            max_min: a list containing the two functions (max and min) used to choose an evaluated move for white and black respectively.
                     this function assumes that the opponent will choose the best move possible to them (according to our model), which will
                     result in them choosing the move with the lowest evaluation.
        """
        path_eval_pairs = [] # Contains tuples of (path, evaluation) pairs

        # First 'move' in tree is 'Start' so need to fudge the colour variable slightly. i.e if colour is 0 (i.e white)
        # Want the colour variable to look like: (move='Start', colour=1) -> (move='e4', colour=0) -> (move='e5', colour=1)
        # Therefore, to keep abstraction, (so you can just pass in self.colour), fudge slightly:
        colour = 1 - colour

        ### First, check if next_moves is empty, if so, just return the path and evaluation
        if tree.is_leaf():
            path = tree.get_path()
            return [(path, model(path))]
        
        ### Now cycle through each child tree of tree
        for child_tree in tree.next_moves:
            # If the child is a leaf, add it's path
            if child_tree.is_leaf():
                path = child_tree.get_path()
                path_eval_pairs.append((path, model(path))) # add path and evaluation to list
            # If the child is not a leaf, now search through the child tree
            else:
                # get_best_evals returns a list, as multiple paths can give the same evaluation.
                # Even if it is just one pair, use a for loop to unpack
                for pair in self.get_best_evals(child_tree, model, (1-colour), max_min): # (1 - colour) as the next move will be the other colour's turn
                    path_eval_pairs.append(pair)
        
        ### Now choose (all of) the best pairs. Need to use list comprehension as there could be multiple values with the same eval.
        # Evaluation is stored in pair[1] so find the best eval with max(path_eval_pairs, key=lambda x: x[1]) and add pair to 'best_pairs' if
        # eval (i.e pair[1]) is the same value.
        best_pairs = [pair for pair in path_eval_pairs if pair[1] == max_min[colour](path_eval_pairs, key=lambda x: x[1])[1]]

        return best_pairs

class ChessPlayer():
    """
    Contains a model, the player's team and a ChessGame instance. Can be used to choose and make a move.

    attr:
        model: the model used to decide the moves the player makes
        team: 0 for white, 1 for black
        game: ChessGame instance containing information about the game.
    """
    def __init__(self, model, colour, game):
        self.model = model
        self.colour = colour
        self.game = game

        self.model.train() # model will only be used in training mode
    
    def choose_move(self, depth):
        """
        Finds all possible moves at a given depth. Then evaluates each path and chooses the most favourable.
        """
        
        ### Update moves_tree with depth
        self.game.update_moves_tree(depth)

        ### Now cycle the tree and choose the best move. NEED TO FIX get_best_evals() to actually play moves to evaluate!
        best_path_eval_pairs = self.game.get_best_evals(self.game.moves_tree, self.model, self.colour)

        ### best_path_eval_pairs can contain multiple pairs, so randomly choose one
        path, eval = random.choice(best_path_eval_pairs)

        ### Then choose the first move from the pair and push it
        self.game.current_position.push(path[1]) # Remembering the first element of path is 'Start'

        return path, eval

class TestModel(torch.nn.Module):
    """
    Test model to test if a game can actually be played.
    """
    def __init__(self):
        super().__init__()

    def forward(self, path):
        # Just randomly chooses a move
        return random.randint(0, 100)


# Generates games given two models

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
    # Setup game board
    game = ChessGame()

    # Setup players
    white_model = TestModel()
    black_model = TestModel()

    white = ChessPlayer(white_model, 0, game)
    black = ChessPlayer(black_model, 1, game)

    for i in range(10):
        # Both players make a move
        white_path, white_eval = white.choose_move(depth=0.5)
        black_path, black_eval = black.choose_move(depth=0.5)

        # Print the moves
        print(f'{i+1}. {white_path[1]} ({white_eval})  {black_path[1]} ({black_eval})')

if __name__ == '__main__':
    #play_game(1, 1, 1)
    """
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
    
    print(moves_tree.nodes[0].nodes[1].print_path())
    """

    play_game(1, 1, 1)