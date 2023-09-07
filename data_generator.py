import chess
import torch

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
                 # append adds a new list in an extra dimension, but here we want to combine two lists along the SAME DIMENSION, so use +
                all_paths += self.get_all_paths(child_tree)
        
        return all_paths

class ChessPlayer():
    """
    Contains a model, the player's team and a ChessGame instance. Can be used to choose and make a move.

    attr:
        model: the model used to decide the moves the player makes
        team: 0 for white, 1 for black
        game: ChessGame instance containing information about the game.
    """
    def __init__(self, model, team, game):
        self.model = model
        self.team = team
        self.game = game

        self.model.train() # model will only be used in training mode
    
    def choose_move(self, depth):
        """
        Finds all possible moves at a given depth. Then evaluates each path and chooses the most favourable.
        """
        
        ### Update move tree with depth
        self.game.update_moves_tree(depth)
        possible_paths = self.game.get_all_paths(self.game.moves_tree)

        ### Now cycle through each path and evaluate it
        path_evals = self.evaluate_paths(possible_paths)

        ### Now choose the move
        

    def evaluate_paths(self, paths):
        """
        Takes in a list of possible paths and evaluates them all
        """
        path_evals = []

        # Cycle through each path and evaluate it
        for path in paths:
            # Make all of the moves, noting that first move is 'Start', so skip it
            for move in path[1:]:
                self.game.push(move)
            # Evaluate the position
            with torch.evaluation_mode():
                path_evals.append(self.model(self.game)) ##### NEEDS TO BE FIXED TO ACCOMODATE MODEL INPUT
            # Undo all moves
            for move in range(len(path) - 1):
                self.game.pop()




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

    # Initialise ChessGame and ChessPlayers
    chess_game = ChessGame()
    player_0 = ChessPlayer(1, 0, chess_game)

    player_0.choose_move(depth=1)