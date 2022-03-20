"""Run game autonomously"""
import importlib  
import os
import sys
import argparse

import tron
from agent.util import build_agent_list

def run_simulation(players: int = 2, size: int = 25, agents: list[str] = ['agent.wallhugger'],
                   fname_root: str = "tron_game"):
    
    print("TRON battle of {} players on {} grid".format(players, size))
    # build agent list
    agent_list = build_agent_list(players, agents)
    print("Competitors: {}".format(agent_list))

    # module_names = [os.path.splitext(a)[0] for a in agent_list]
    agent_modules = [importlib.import_module(a) for a in agent_list]

    # instantiate the game
    game = tron.Tron(size=size, num_players=players)
    observation = game.reset()

    done = False
    while not done:
        # generate all the actions
        actions = [am.generate_move(observation['board'],
                                    observation['positions'],
                                    observation['orientations'],
                                    uid) for uid, am in enumerate(agent_modules)]
        observation, done, status, reward = game.move(*actions)

    
    # determine the winner and print
    filename = game.save(fname_base=fname_root)
    print("Finished - game saved to {}".format(filename))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TRON - AI battle using provided agents")
    parser.add_argument('--players', '-p', type=int, help="Number of players", default=2)
    parser.add_argument('--size', '-s', type=int, help="Size of grid", default=100)
    parser.add_argument('--fname_root', '-f', type=str, default="tron_game", help="Filename root for saving game")
    parser.add_argument('agents', nargs='*', default=['agent.wallhugger',], help="module to use, e.g. agent.dumb")
    args = parser.parse_args()
    
    run_simulation(players=args.players,
                   size=args.size,
                   agents=args.agents,
                   fname_root=args.fname_root)
