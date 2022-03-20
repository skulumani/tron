"""Monte Carlo learning for Tron"""
import argparse
import json
import os
from typing import Dict, Optional, Any
import importlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import tron
from agent.util import build_agent_list

class MonteCarlo:
    
    ACTION_MAP = {tron.Turn.LEFT_90: 0, tron.Turn.STRAIGHT: 1, tron.Turn.RIGHT_90: 2}
    DIRECTION_MAP = {v: k for k, v in ACTION_MAP.items()}

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

   
        # Q, N, and game stats data
        self.q_table: Optional[np.ndarray] = None
        self.n_table: Optional[np.ndarray] = None
        self.game_stats: Optional[pd.DataFrame] = None

        self._load_qn_tables()
        # TODO Verify loading/saving of game stats and Q/N tables
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
            self.q_table = self._initialize_table(self.vision_grid_size, dtype=float)
            self.n_table = self._initialize_table(self.vision_grid_size, dtype=int)

    def _initialize_table(self, vision_grid_size: int, dtype) -> np.ndarray:
        """Initialize Q and N tables"""
        size = tuple([2 for ii in range(vision_grid_size**2)]) + tuple([len(tron.Turn)])
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

    def select_action(self, state) -> tron.Turn:
        """Pick best action from Q table"""
        idx_a = np.argmax(self.q_table[tuple(state)])
        x = np.random.random()
        if x > self.epsilon:
            return self.DIRECTION_MAP[idx_a]
        else:
            return self.DIRECTION_MAP[np.random.choice(len(self.DIRECTION_MAP))]

    def update_table(self, trajectory: Dict[str, Any]) -> None:
        states = trajectory["states"]
        actions = trajectory["actions"]
        rewards = trajectory["rewards"]

        state_action_pairs = [(s, a) for s, a in zip(states, actions)]

        g = 0
        for ii in reversed(range(len(states))):
            s = states[ii]
            a = actions[ii]
            r = rewards[ii]

            g = r + self.discount_rate * g
            if (s, a) in state_action_pairs[:ii]:
                continue
            idx = tuple(s) + (self.ACTION_MAP[a],)
            self.n_table[idx] += 1
            self.q_table[idx] = self.q_table[idx] + 1/self.n_table[idx] * (g - self.q_table[idx])

    @staticmethod
    def _build_game_stats(n: int, game_stats: Dict) -> Dict:
        stats = {"episode": n}  
        stats.update(game_stats)
        return stats

    def run_simulation(self, num_episodes: int = 1000, game_save_modulo: int = 500):

        stats = []
        for n_sim in range(num_episodes):
            
            game = tron.Tron(size=self.size, num_players=self.players)
            observation = game.reset()

            done = False
        
            trajectory = {"states": [], "actions": [], "rewards": []}
            while not done:
                # get current state representation (vision grid)
                s = game.get_vision_grid(uid=1, size=self.vision_grid_size)
                trajectory["states"].append(s)

                action = self.select_action(s) # pick action based on current state
                trajectory["actions"].append(action)

                # RL agent is player uid=1 (first player always)
                actions = [action]
                # actions for players uid > 1
                actions = actions + [am.generate_move(observation['board'],
                                                    observation['positions'],
                                                    observation['orientations'],
                                                    ii+1) for ii, am in enumerate(self.agents)]

                # game move
                observation, done, status, reward = game.move(*actions)
                trajectory["rewards"].append(reward[0]) # reward for first player
            
            # self.game.get_game_state()
            # save total game state and update table
            self.update_table(trajectory)
            stats.append(self._build_game_stats(n=0, game_stats=self.game.get_game_stats(uid=1))) # RL is player uid=1
  
        # save learning statistics
        # TODO Verify the saving/loading here
        # self.game_stats = pd.concat([self.game_stats, pd.DataFrame.from_records(stats)], ignore_index=True)
        # self.game_stats.to_csv(self._game_stats_fn, index=False)

        # # save Q and N tables
        # with open(self._qn_tables_fn, "w") as fp:
        #     json.dump({'q_table': self.q_table, 'n_table': self.n_table}, fp, indent=4, cls=NumpyEncoder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MONTE CARLO TRON - Learning using Monte Carlo on-policy")
    parser.add_argument('--players', '-p', type=int, help="Number of players - default 2", default=2)
    parser.add_argument('--size', '-s', type=int, help="Size of game grid - default 25", default=25)
    parser.add_argument('--vision_grid', '-v', type=int, help="Size of vision grid - default 3. Must be odd", default=3)
    parser.add_argument('agents', nargs="*", default=['agent.semideterministic'], help="Opponent modules, e.g. agent.dumb")
    args = parser.parse_args()

    rl_agent = MonteCarlo(players=args.players, size=args.size, agents=args.agents,
                          vision_grid_size=args.vision_grid)
    rl_agent.run_simulation()
    # rl_agent.visualize_learning()
