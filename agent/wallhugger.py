"""Go straight unless there's an obstacle"""
import numpy as np

import tron
from agent.util import get_valid_moves, validate_move


def generate_move(board, positions, orientations, uid):
    """Generate move for game

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
    # current player state
    y, x = positions[uid]
    orientation = orientations[uid]
    
    # try to go straight
    if validate_move(y, x, orientation, board, action=tron.Turn.STRAIGHT):
        move = tron.Turn.STRAIGHT
    else:
        # check all moves and determine if they result in collision
        valid_moves = get_valid_moves(y, x, orientation, board)

        if valid_moves:
            move = np.random.choice(valid_moves)
        else:
            move = np.random.choice(tron.Turn)
            
        # try to move straight

    return move


