"""Run game autonomously"""
import importlib  
import os
import sys
import argparse

import tron

def run_simulation(players, size, agents):
    
    print("TRON battle of {} players on {} grid".format(players, size))

    # build agent list
    if len(agents) < players:
        print("Insufficient agents provided. Will duplicate last agent")
        agent_list = agents
        for ii in range(len(agents), players):
            agent_list.append(agents[-1])
    elif len(agents) == 1:
        agent_list = [agents for ii in range(players)]
    elif len(agents) > players:
        agent_list = [agents for ii in range(players)]
    else:
        print("Something strange with agent list")
        return 1
    
    print("Competitors: {}".format(agent_list))
    
    module_names = [os.path.splitext(a)[0] for a in agent_list]
    agent_modules = [importlib.import_module(a) for a in module_names]

    # instantiate the game
    game = tron.Tron(size=size, num_players=players)
    observation = game.reset()

    done = False
    while not done:
        # generate all the actions
        actions = [am.generate_move(observation['board'],
                                    observation['positions'],
                                    observation['orientations']) for am in agent_modules]
        observation, done, status = game.move(*actions)

    
    # determine the winner and print
    filename = game.save()
    print("Finished - game saved to {}".format(filename))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TRON - AI battle using provided agents")
    parser.add_argument('--players', '-p', type=int, help="Number of players", default=2)
    parser.add_argument('--size', '-s', type=int, help="Size of grid", default=100)
    parser.add_argument('agents', nargs='*', default='dumb_agent.py', help="module filename of agents to battle")
    args = parser.parse_args()
    
    run_simulation(players=args.players,
                   size=args.size,
                   agents=args.agents)
