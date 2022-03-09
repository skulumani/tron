import numpy as np
import tron

def generate_move(board, positions, orientations):
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
    
    # check all moves and determine if they result in collision

    # pick a random move that doesn't cause a collision
    pass


