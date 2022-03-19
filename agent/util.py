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

def build_agent_list(players: int, agents: list[str]) -> list[str]:
    
    if len(agents) < players:
        print("Insufficient agents provided. Will duplicate last agent")
        agent_list = agents
        for ii in range(len(agents), players):
            agent_list.append(agents[-1])
    elif len(agents) == 1:
        agent_list = [agents[0] for ii in range(players)]
    elif len(agents) >= players:
        agent_list = [agents[ii] for ii in range(players)]
    else:
        print("Something strange with agent list - using default")
        agent_list = ["agent.semideterministic" for ii in range(players)]

    return agent_list
