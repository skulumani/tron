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

    move = get_forward_command()
    # move = get_stochastic_command()
    return move

def get_forward_command():
    """Just go forward"""
    move = tron.Turn.STRAIGHT
    return move

def get_stochastic_command():
    """Go forward mostly but sometimes turn"""
    rand = np.random.rand()
    if rand < 0.1:
        move = tron.Turn.LEFT_90
    elif rand > 0.9:
        move = tron.Turn.RIGHT_90
    else:
        move = tron.Turn.STRAIGHT

    return move
