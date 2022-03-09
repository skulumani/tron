"""Randomly pick only valid moves"""

import numpy as np
import tron

def generate_move(board, positions, orientations):
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
    # assume that current player is always player 0
    y, x = positions[0]
    orientation = orientations[0]
    # get list of possible moves
    valid_moves = []
    for a in tron.Turn:
        (yn, xn, _) = tron.Player.future_move(y, x, orientation, a)

        # check if resulting square is occupied
        if tron.Tron.validate_position(yn, xn, board):
            valid_moves.append(a)

    # randomly pick a move from valid options - or if none pick a random invalid one
    if valid_moves:
        move = np.random.choice(valid_moves)
    else:
        move = np.random.choice(tron.Turn)

    return tron.Turn(move)
