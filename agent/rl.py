"""Reinforcement Learning based agent
"""
import numpy as np

import tron
from agent.util import get_valid_moves, validate_move


def generate_move(board: np.ndarray, positions: list, orientations: list, uid: int) -> tron.Turn:

    # load the Q table from Json

    # pick best action based on epsilon greedy approach

    # consider validating move (reject obvious crashes)
    pass


