Contains ideas for how to approach problems.

# Data Generation

Could:
(a):
    - Play games
    - Use result of game to reward/punish model based on outcome
(b):
    - Play games
    - Use board position at given move and outcome to predict what is a good and bad move.

+(a): Easier, more logical concept
+(b): Consistent input size to model


DO I WANT A MODEL WHICH:

takes in chess position -> evaluates position? (b)

takes in chess position -> evaluates position -> evaluates moves -> chooses best move (a)

LET'S START WITH (b)

# Tree pruning

At each level, evaluate all possible positions

[('movea', evala), ('moveb', evalb), etc.]

Then choose all moves for which the eval >= prev_eval - tol

If no such moves exist, choose the best move and return it

else return the full list

OR choose top n moves in each list

OR allow the program to search the tree for n seconds, starting with the most promising moves