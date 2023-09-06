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