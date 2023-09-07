import chess

class MoveTree():
    """A tree containing all possible moves up to a certain depth"""
    def __init__(self, move, parent=None):
        self.move = move
        self.nodes = []
        self.parent = parent

    def add_node(self, move):
        self.nodes.append(MoveTree(move, parent=self))
    
    def __repr__(self):
        return f"MoveTree({self.move}): {self.nodes}"
    
    def is_leaf(self):
        # If nodes list is empty, return true.
        # bool of an empty list == false, so return not bool(list)
        return not bool(self.nodes)
    
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

class TestTree():
    """A test tree for testing find_possible_moves in ChessGame class."""
    def __init__(self, move, parent=None):
        self.move = move
        self.next_moves = []
        self.parent = parent

    def add_node(self, move):
        self.next_moves.append(TestTree(move, parent=self))
    
    def __repr__(self):
        return f"MoveTree({self.move}): {self.next_moves}"
    
    def is_leaf(self):
        # If nodes list is empty, return true.
        # bool of an empty list == false, so return not bool(list)
        return not bool(self.next_moves)
    
    def legal_moves(self):
        return [0, 1]

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
    """
    def __init__(self):
        self.current_position = chess.Board() # initialise with default position

        self.moves_tree = self.find_possible_moves(depth=3, tree=TestTree('Start'))

    def find_possible_moves(self, depth, tree):
        """
        Finds all moves up to a given depth. Returns the tree object.
        """

        if depth > 0:
            # Find all the legal moves at this level and append to nodes
            for move in tree.legal_moves():
                tree.add_node(move)
            # Now cycle through each node at the current level and find new nodes a level deeper
            for new_tree in tree.next_moves:
                self.find_possible_moves(depth-1, new_tree)
        
        return tree
    
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
                 # append adds a new list in an extra dimension, but here we want to combine two lists along the SAME DIMENSION, so us +
                all_paths += self.get_all_paths(child_tree)
        
        return all_paths

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

    example = ChessGame()

    for path in example.get_all_paths(example.moves_tree):
        print(path)