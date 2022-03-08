import numpy as np
import tron

def generate_move(board, positions, orientation):
    """

    Args:
        board (np.array): game board as nd array
            [:, :, 0]: obstacles
            [:, :, 1:]: player locations
        positions (list): list of current position of self and opponents as tuple (y, x)
        orientations (list): list of self orientation and opponents
            from tron.Orientation
    
    Returns:
        move (int): Integer move command from tron.Turn
    """
    pass

def get_valid_moves(board, positions, orientation):
    # get list of possible moves
    for a in tron.Turn:
        (yn, xn, _) = tron.Player.future_move(y, x, orientation, a)

        # check if resulting square is occupied

        # check all moves for future collisions

    # randomly pick a move from valid options - or if none pick a random invalid one

    pass
