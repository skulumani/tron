import numpy as np

import tron

def get_valid_moves(y: int, x: int, orientation: tron.Orientation,
                    board: np.ndarray) -> list[tron.Turn]:
    valid_moves = []
    for a in tron.Turn:
        (yn, xn, _) = tron.Player.future_move(y, x, orientation, a)

        # check if resulting square is occupied
        if tron.Tron.validate_position(yn, xn, board):
            valid_moves.append(a)

    return valid_moves

def validate_move(y: int, x: int, orientation: tron.Orientation, 
                  board: np.ndarray, action: tron.Turn) -> bool:
    (yn, xn, _) = tron.Player.future_move(y, x, orientation, tron.Turn.STRAIGHT)
    return tron.Tron.validate_position(yn, xn, board)
