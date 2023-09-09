import chess
import torch
import random

import variables
import model_builder

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
        self.current_position = TensorBoard() # initialise with default position
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
                #print(path_eval_pairs[-1])
            # If the child is not a leaf, now search through the child tree
            else:
                # get_best_evals returns a list, as multiple paths can give the same evaluation.
                # Even if it is just one pair, use a for loop to unpack
                for pair in self.get_best_evals(child_tree, model, 1-colour, max_min): # (1 - colour) as the next move will be the other colour's turn
                    path_eval_pairs.append(pair)
                    #print(pair)

            self.current_position.pop() # unmake the move (required for evaluation)
        
        ### Now choose (all of) the best pairs. Need to use list comprehension as there could be multiple values with the same eval.
        # Evaluation is stored in pair[1] so find the best eval with max(path_eval_pairs, key=lambda x: x[1]) and add pair to 'best_pairs' if
        # eval (i.e pair[1]) is the same value.
        if tree.move == 'Start':
            for pair in path_eval_pairs:
                print(pair)
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

class TensorBoard(chess.Board):
    """
    Extension of chess.Board class that also has the capability of converting the current position to a tensor.
    """
    def __init__(self):
        super().__init__()

    def as_tensor(self):
        """
        Returns a flattened tensor representation of the board.

        returns:
            board_as_tensor: a 70 length vector. Indices 0-63 correspond to the current board position.
                             index 64 corresponds to the turn (i.e white=0, black=1)
                             index 65, 66, 67 and 68 indicate whether white and black can castle king and queenside respectively, 1 for true, 0 for false.
                             index 69 indicates if en-passant is legal and if so, which square. -1 indicates no en-passant possible 
        """
        fen = self.fen(promoted=False)
        board_position, turn, castling_rights, ep_square = fen.split(' ')[:-2]

        ### Format the board position
        for i in range(8):
            board_position = board_position.replace(str(i+1), ''.join(['0' for _ in range(i+1)])) # Replace all integers with that many 0s
        board_position = list(board_position.replace('/', '')) # remove the slashes from board_position
        board_position = list(map(self.fen_to_number, board_position)) # now convert FEN letters to my integer representation (see variables.py)

        ### Format the turn
        turn = [0 if turn == 'w' else 0]

        ### Format the castling_rights
        castle_check = ['K', 'Q', 'k', 'q']
        # Check if 'castling_rights' contains 'K' etc. If so, add 1 to list, else 0
        castling_rights = [int(castling_rights.__contains__(check_letter)) for check_letter in castle_check]

        ### Format the en-passant
        # En-passant is in the form '-' if false and the square (e.g e6) if true
        ep_square = 'e6'
        ep_square = [-1 if ep_square == '-' else self.convert_square_to_index(ep_square)]

        ### Concatenate them all. All lists so can just use +
        combined = board_position + turn + castling_rights + ep_square

        return torch.tensor(combined)

    def fen_to_number(self, char: str):
        """
        Converts a fen value e.g [P, R, N, Q] into my number representation e.g [1, 4, 2, 5]
        """
        if char.isdigit(): # i.e if it just represents a number of empty squares
            return int(char)

        # If not, translate
        return variables.fen_number_translation[char]

    def convert_square_to_index(self, square):
        """
        Takes a square in algebraic notation (e.g e6) and converts it to an index from 0 to 63
        """
        # Split the square into a file and a rank
        file, rank = list(square)
        
        # Convert file to a number
        file = variables.file_to_number[file]

        # Now convert to an index. The FEN representation puts a1 at the END of the list, so keep that representation
        # Therefore, 'a8' is index 0, 'h8' is index 7, 'h1' is index 63.

        return 8 * (8 - int(rank) ) + file - 1

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
        move = input(f"Opponent played {white_path[1]} with eval={white_eval}. Choose your move: ")

        # Make your move
        game.current_position.push_san(move)

        # Print move info
        print(f'{i+1}. {white_path[1]} ({white_eval}) {move}')
        print(model(game.current_position.as_tensor()))

if __name__ == '__main__':

    base_model = model_builder.BaseModel(variables.material_values)

    play_against_model(base_model, depth=1)

