import chess
import my_chess
import torch
import random
import numpy as np

import variables
import model_builder

from operator import add, ge, le

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
        self.path = self.get_path()

    def add_node(self, move):
        self.next_moves.append(MoveTree(move, parent=self))

    def add_nodes(self, moves):
        # Appends multiple nodes using list comp
        self.next_moves += [MoveTree(move, parent=self) for move in moves]
    
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
        self.current_position = my_chess.TensorBoard() # initialise with default position
        self.moves_tree = MoveTree('Start') # Just a placeholder

    def find_possible_moves(self, depth, tree):
        """
        Finds all moves up to a given depth. Returns the tree object.
        """

        if depth > 0:
            # Find all the legal moves at this level and append to nodes
            tree.add_nodes(list(self.current_position.legal_moves))
            # Now progress to next level and cycle through each node at the current level and find new nodes a level deeper
            for new_tree in tree.next_moves:
                self.current_position.push(new_tree.move) # progress to next move
                self.find_possible_moves(depth - 0.5, new_tree)
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
            colour: the team of the model - 0 for white, 1 for black
            max_min: a list containing the two functions (max and min) used to choose an evaluated move for white and black respectively.
                     this function assumes that the opponent will choose the best move possible to them (according to our model), which will
                     result in them choosing the move with the lowest evaluation.
        """
        path_eval_pairs = [] # Contains tuples of (path, evaluation) pairs

        ### First, check if next_moves is empty, if so, just return the path and evaluation
        if tree.is_leaf():
            path = tree.get_path()
            return [(path, model(self.current_position.as_tensor()))]
        
        ### Now cycle through each child tree of tree
        for child_tree in tree.next_moves:
            self.current_position.push(child_tree.move) # make the move (required for evaluation)

            # If the child is a leaf, add it's path
            if child_tree.is_leaf():
                path = child_tree.get_path()
                path_eval_pairs.append((path, model(self.current_position.as_tensor()))) # add path and evaluation to list
            # If the child is not a leaf, now search through the child tree
            else:
                # get_best_evals returns a list, as multiple paths can give the same evaluation.
                # Even if it is just one pair, use a for loop to unpack
                for pair in self.get_best_evals(child_tree, model, 1-colour, max_min): # (1 - colour) as the next move will be the other colour's turn
                    path_eval_pairs.append(pair)

            self.current_position.pop() # unmake the move (required for evaluation)
        
        ### Now choose (all of) the best pairs. Need to use list comprehension as there could be multiple values with the same evaluation.
        # Evaluation is stored in pair[1] so find the best evaluation with max(path_eval_pairs, key=lambda x: x[1]) and add pair to 'best_pairs' if
        # evaluation (i.e pair[1]) is the same value.
        max_min_eval = max_min[colour](path_eval_pairs, key=lambda x: x[1])[1]
        best_pairs = [pair for pair in path_eval_pairs if pair[1] == max_min_eval]

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
        path, evaluation = random.choice(best_path_eval_pairs)

        ### Then choose the first move from the pair and push it
        self.game.current_position.push(path[1]) # Remembering the first element of path is 'Start'

        return path, evaluation

class ChessGameV2():
    """
    Contains the information for a single chess game, including the function to search for moves up to a certain depth.

    attr:
        current_position: A chess.Board instance that contains the current position of the game. Is also used to find all possible moves
        moves_tree: A MoveTree() instance that contains all of the possible moves up to a certain depth.
    """
    def __init__(self):
        self.current_position = my_chess.TensorBoard() # initialise with default position
        self.moves_tree = MoveTree('Start') # Just a placeholder
    
    def get_best_evals(self, tree, depth, model, colour, max_min=[max, min], ge_le=[ge, le], prev_eval=0):
        """Searches and builds each tree and finds evaluation. If it is a evaluation < previous evaluation, discard the move.
        Repeat until the best evaluation is returned.

        args:
            tree: the current MoveTree object
            depth: the depth of the current tree
            prev_eval: the previous evaluation of the tree. Defaults to 0
            model: the model used to evaluate the moves
            colour: the team of the model - 0 for white, 1 for black
            max_min: a list containing the two functions (max and min) used to choose an evaluated move for white and black respectively.
                     this function assumes that the opponent will choose the best move possible to them (according to our model), which will
                     result in them choosing the move with the lowest evaluation.
        """
        # Check we haven't reached the bottom of the tree
        if depth > 0:
            # If tree is not a leaf, find evaluations and add all positive evaluations to tree
            if bool(self.current_position.legal_moves):
                # Now find all evaluations
                path_eval_pairs = []
                current_best_eval = -500 # arbitrarily low number
                for move in self.current_position.legal_moves:
                    self.current_position.push(move) # make the move
                    evaluation = model(self.current_position.as_tensor()) # evaluate the move
                    if ge_le[colour](evaluation, prev_eval): # i.e choose the 'best'
                        # If move is valid, search that tree
                        tree.add_node(move)

                        path_eval_pairs = self.search_subtree(tree, path_eval_pairs, model, depth, colour, max_min, evaluation)
                    elif ge_le[colour](evaluation, current_best_eval): # Also check if it is better than the current best
                        current_best_eval = evaluation # update evaluation
                        current_best_move = move # save the move
                    
                    if not bool(tree.next_moves): # i.e if there are no positions better than prev_eval
                        tree.add_node(move)

                        path_eval_pairs = self.search_subtree(tree, path_eval_pairs, model, depth, colour, max_min, evaluation)

                    self.current_position.pop() # unmake the move
                
                ### Now choose (all of) the best pairs. Need to use list comprehension as there could be multiple values with the same evaluation.
                # Evaluation is stored in pair[1] so find the best evaluation with max(path_eval_pairs, key=lambda x: x[1]) and add pair to 'best_pairs' if
                # evaluation (i.e pair[1]) is the same value.
                max_min_eval = max_min[colour](path_eval_pairs, key=lambda x: x[1])[1]
                best_pairs = [pair for pair in path_eval_pairs if pair[1] == max_min_eval]

                return best_pairs
            else: # i.e if the tree is a leaf
                return [[tree.path, model(self.current_position.as_tensor())]]
        else: # i.e if we are at the final depth
            # Move has already been made
            return [[tree.path, model(self.current_position.as_tensor())]]

    def search_subtree(self, tree, path_eval_pairs, model, depth, colour, max_min, evaluation):
        # If the child is a leaf, add it's path
        if not bool(self.current_position.legal_moves):
            path = tree.next_moves[-1].get_path() # next_moves[-1] contains the tree just added
            path_eval_pairs.append((path, model(self.current_position.as_tensor()))) # add path and evaluation to list
        # If the child is not a leaf, now search through the child tree
        else:
            # get_best_evals returns a list, as multiple paths can give the same evaluation.
            # Even if it is just one pair, use a for loop to unpack
            # (1 - colour) as the next move will be the other colour's turn
            for pair in self.get_best_evals(tree.next_moves[-1], depth-0.5, model, 1-colour, max_min, prev_eval=evaluation):
                path_eval_pairs.append(pair)

        return path_eval_pairs
    
class ChessPlayer2():
    def __init__(self, model, colour, game):
        self.model = model
        self.colour = colour
        self.game = game

        self.model.train() # model will only be used in training mode

    def choose_move(self, depth):
        """
        Finds all possible moves at a given depth. Then evaluates each path and chooses the most favourable.
        """

        ### Now cycle the tree and choose the best move. NEED TO FIX get_best_evals() to actually play moves to evaluate!
        best_path_eval_pairs = self.game.get_best_evals(self.game.moves_tree, depth, self.model, self.colour)

        ### best_path_eval_pairs can contain multiple pairs, so randomly choose one
        path, evaluation = random.choice(best_path_eval_pairs)

        ### Then choose the first move from the pair and push it
        self.game.current_position.push(path[1]) # Remembering the first element of path is 'Start'

        return path, evaluation
    
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
    white_model = model
    black_model = base_model

    white = ChessPlayer(white_model, 0, game)
    black = ChessPlayer(black_model, 1, game)

    for i in range(10):
        # Both players make a move
        white_path, white_eval = white.choose_move(depth=0.5)
        black_path, black_eval = black.choose_move(depth=0.5)

        # Print the moves
        print(f'{i+1}. {white_path[1]} ({white_eval})  {black_path[1]} ({black_eval})')

def play_against_model(model, depth):
    """
    Play a game against a model.

    args:
        depth: how far the model searches to evaluate positions
    returns:
        game_moves: a movetext including all moves
    """

    # Setup game board
    game = ChessGame()

    # Setup opponent
    opponent = ChessPlayer(model, 0, game)

    for i in range(10):
        # Opponent makes a move
        white_path, white_eval = opponent.choose_move(depth=1)

        # Now user makes a move
        move = input(f"Opponent played {white_path[1]} with evaluation={white_eval}. Choose your move: ")

        # Make your move
        game.current_position.push_san(move)

        # Print move info
        print(f'{i+1}. {white_path[1]} ({white_eval}) {move}')

if __name__ == '__main__':

    base_model = model_builder.BaseModel(variables.material_values)

    
    #play_against_model(base_model, depth=2)

    """
    # Setup instances
    game = ChessGame()
    player = ChessPlayer(base_model, 0, game)

    # Make evaluation
    white_path, white_eval = player.choose_move(depth=3)

    # Print evaluation
    print(f"Opponent played {white_path[1]} with evaluation={white_eval}.")
    """

    # Setup instances
    game = ChessGameV2()
    player = ChessPlayer2(base_model, 0, game)

    # Make evaluation
    white_path, white_eval = player.choose_move(depth=2)

    # Print evaluation
    print(white_path)
    print(f"Opponent played {white_path[1]} with evaluation={white_eval}.")


    



