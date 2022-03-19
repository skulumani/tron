"""Monte Carlo learning for Tron"""
import argparse
import json
import os
from typing import Dict, Optional
import importlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import tron
from agent.util import build_agent_list

class MonteCarlo:

    def __init__(self, players: int = 2, size: int = 25, 
                 agents: str = 'agent.semideterministic',
                 discount_rate: float = 0.9, epsilon: float = 0.2, filename_root: str = None,
                 vision_grid_size: int = 3):
        self.players = players
        self.size = size
        self.discount_rate = discount_rate # future reward value
        self.epsilon = epsilon # greedy selection probability
        
        self.vision_grid_size = vision_grid_size
        # filenames for storing data
        fname_root = (f'tron_mc_{self.size}x{self.size}_{self.players}players' if not filename_root else filename_root)
        self._qn_fname = f'{fname_root}_qn_tables.json'
        self._game_stats_fname = f'{fname_root}_game_stats.csv'

        self.agent_list = build_agent_list(self.players-1, agents)
        self.agents = [importlib.import_module(a) for a in agents]

        self.game = tron.Tron(size=self.size, num_players=self.players)
   
        # Q, N, and game stats data
        self.q_table: Optional[np.ndarray] = None
        self.n_table: Optional[np.ndarray] = None
        self.game_stats: Optional[pd.DataFrame] = None

        self._load_qn_tables()
        # self._load_game_stats()

    def _load_qn_tables(self) -> None:
        if os.path.exists(self._qn_fname):
            print("Loading saved Q and N tables")
            with open(self._qn_fname, "r") as f:
                table = json.load(f)
                self.q_table = np.array(table['q_table'], dtype=float)
                self.n_table = np.array(table['n_table'], dtype=int)
        else: # no saved data
            print("Intializing new Q and N tables")
            self.q_table = self._intialize_table(self.vision_grid_size, dtype=float)
            self.n_table = self._intialize_table(self.vision_grid_size, dtype=int)

    
    def _initialize_table(self, vision_grid_size: int = 3, dtype) -> np.ndarray:
        """Initialize Q and N tables"""
        size = tuple([2 for ii in range(vision_grid_size**2)])
        table = np.zeros(size, dtype=dtype)
        return table
    
    def _load_game_stats(self) -> None:
        if os.path.exists(self._game_stats_fname):
            print("Loading saved game stats")
            self.game_stats = pd.read_csv(self._game_stats_fname)
        else:
            print("Initializing game stats")
            # TODO Decide on what game stats to save
            # self.game_stats = pd.DataFrame(columns=[])


    def run_simulation(self):
        observation = self.game.reset()
        done = False

        while not done:
            # RL agent is player 0
            actions = [tron.Turn.STRAIGHT]
            # actions for players > 0
            actions = actions + [am.generate_move(observation['board'],
                                                  observation['positions'],
                                                  observation['orientations'],
                                                  ii+1) for ii, am in enumerate(self.agents)]

            # game move
            observation, done, status, reward = self.game.move(*actions)
        
        # save total game state and update table
        print('Finished game')



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MONTE CARLO TRON - Learning using Monte Carlo on-policy")
    parser.add_argument('--players', '-p', type=int, help="Number of players - default 2", default=2)
    parser.add_argument('--size', '-s', type=int, help="Size of grid - default 25", default=25)
    parser.add_argument('agents', nargs="*", default=['agent.semideterministic'], help="Opponent modules, e.g. agent.dumb")
    args = parser.parse_args()

    rl_agent = MonteCarlo(players=args.players, size=args.size, agents=args.agents)
    rl_agent.run_simulation()
    # rl_agent.visualize_learning()
