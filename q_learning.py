"""Q learning for Tron"""
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
from utilities import NumpyEncoder

class QLearning:
    
    ACTION_MAP = {tron.Turn.LEFT_90: 0, tron.Turn.STRAIGHT: 1, tron.Turn.RIGHT_90: 2}
    DIRECTION_MAP = {v: k for k, v in ACTION_MAP.items()}

    def __init__(self, players: int = 2, size: int = 25, 
                 agents: str = 'agent.wallhugger', learning_rate: float = 0.4,
                 discount_rate: float = 0.9, epsilon: float = 0.2, 
                 filename_root: str = None, vision_grid_size: int = 3):
        self.players = players
        self.size = size
        self.discount_rate = discount_rate # future reward value
        self.learning_rate = learning_rate 
        self.epsilon = epsilon # greedy selection probability
        
        self.vision_grid_size = vision_grid_size
        # filenames for storing data
        self.fname_root = (f'tron_mc_{self.size}x{self.size}_{self.players}players' if not filename_root else filename_root)
        self._qn_fname = f'{self.fname_root}_q_tables.json'
        self._game_stats_fname = f'{self.fname_root}_game_stats.csv'

        self.agent_list = build_agent_list(self.players-1, agents)
        self.agents = [importlib.import_module(a) for a in agents]

        # Q, N, and game stats data
        self.q_table: Optional[np.ndarray] = None
        self.game_stats: Optional[pd.DataFrame] = None

        self._load_qn_tables()
        self._load_game_stats()

    def _load_qn_tables(self) -> None:
        if os.path.exists(self._qn_fname):
            print("Loading saved Q tables")
            with open(self._qn_fname, "r") as f:
                table = json.load(f)
                self.q_table = np.array(table['q_table'], dtype=float)
        else: # no saved data
            print("Intializing new Q tables")
            self.q_table = self._initialize_table(self.vision_grid_size, dtype=float)
    
    def _load_game_stats(self) -> None:
        if os.path.exists(self._game_stats_fname):
            print("Loading saved game stats")
            self.game_stats = pd.read_csv(self._game_stats_fname)
        else:
            print("Initializing new game stats")
            self.game_stats = pd.DataFrame(columns=['episode',
                                                    'num_actions',
                                                    'total_reward',
                                                    'crash_flag'])

    def _initialize_table(self, vision_grid_size: int, dtype) -> np.ndarray:
        """Initialize Q tables"""
        size = tuple([2 for ii in range(vision_grid_size**2)]) + tuple([len(tron.Turn)])
        table = np.zeros(size, dtype=dtype)
        return table
    
    def select_action(self, state) -> tron.Turn:
        """Pick best action from Q table"""
        idx_a = np.argmax(self.q_table[tuple(state)])
        x = np.random.random()
        if x > self.epsilon:
            return self.DIRECTION_MAP[idx_a]
        else:
            return self.DIRECTION_MAP[np.random.choice(len(self.DIRECTION_MAP))]

    def update_table(self, s: list, a: tron.Turn, r: int, s_prime: list) -> None:
        sa = tuple(s) + (self.ACTION_MAP[a],)
        q_sa = self.q_table[sa]
        q_sp = np.max(self.q_table[tuple(s_prime)])
        self.q_table[sa] = q_sa + self.learning_rate * (r + self.discount_rate * q_sp - q_sa)

    @staticmethod
    def _build_game_stats(n: int, game_stats: Dict) -> Dict:
        stats = {"episode": n}  
        stats.update(game_stats)
        return stats

    def run_simulation(self, num_episodes: int = 1000, game_save_modulo: int = 500):

        stats = []
        n_prev = self.game_stats.shape[0]
        for n_sim in range(num_episodes):
            if (n_sim + 1) % 100 == 0:
                print(f"Simulation {n_sim + 1}/{num_episodes}")

            game = tron.Tron(size=self.size, num_players=self.players)
            observation = game.reset()

            done = False
        
            while not done:
                # get current state representation (vision grid)
                s = game.get_vision_grid(uid=1, size=self.vision_grid_size)

                action = self.select_action(s) # pick action based on current state

                # RL agent is player uid=1 (first player always)
                actions = [action]
                # actions for players uid > 1
                actions = actions + [am.generate_move(observation['board'],
                                                    observation['positions'],
                                                    observation['orientations'],
                                                    ii+1) for ii, am in enumerate(self.agents)]

                # game move
                observation, done, status, reward = game.move(*actions)
                r = reward[0] # we're player 0
                s_prime = game.get_vision_grid(uid=1, size=self.vision_grid_size)
                self.update_table(s=s, a=action, r=r, s_prime=s_prime)
            
            # save total game state and update table
            stats.append(self._build_game_stats(n=n_sim+n_prev, game_stats=game.get_game_stats(uid=1))) # RL is player uid=1

            if (n_sim + 1) % game_save_modulo == 0:
                game_fname = f"{self.fname_root}_episode_{n_prev + n_sim+1}"
                print("Game saved: {}".format(game.save(fname_base=game_fname)))

  
        # save learning statistics
        # TODO Verify the saving/loading here
        self.game_stats = pd.concat([self.game_stats, pd.DataFrame.from_records(stats)], ignore_index=True)
        self.game_stats.to_csv(self._game_stats_fname, index=False)

        # save Q and N tables
        with open(self._qn_fname, "w") as fp:
            json.dump({'q_table': self.q_table}, fp, indent=4, cls=NumpyEncoder)
        
    def visualize_learning(self):
        """Load learning history and plot data"""
        num_episodes = self.game_stats.shape[0]
        episodes = self.game_stats['episode']
        num_actions = self.game_stats['num_actions']
        total_reward = self.game_stats['total_reward']
        crash_flag = self.game_stats['crash_flag']
        unique, counts = np.unique(crash_flag, return_counts=True)
        crash_count = dict(zip(unique, counts))

        print(f"{num_episodes} episodes on {self.size}x{self.size} board")
        print(f"Actions:")
        print(f"    Max: {np.max(num_actions)}")
        print(f"    Avg: {np.mean(num_actions)}")
        print(f"    Min: {np.min(num_actions)}")
        print(f"Rewards:")
        print(f"    Max: {np.max(total_reward)}")
        print(f"    Avg: {np.mean(total_reward)}")
        print(f"    Min: {np.min(total_reward)}")
        print(f"Crash Flag:")
        for cf, num in zip(unique, counts):
            print(f"    {tron.Status(cf).name}: {(num/sum(counts)):.2%} or {num}/{sum(counts)}")
        # print(f"    {: {tron.Status(unique[0]).name} with {counts[0]}/{sum(counts)} occurences")
        # print(f"    Min: {tron.Status(unique[-1]).name} with {counts[-1]}/{sum(counts)} occurences")
        print(f"Reward Table")
        print(f"    Max: {np.max(self.q_table)}")
        print(f"    Avg: {np.mean(self.q_table)}")
        print(f"    Min: {np.min(self.q_table)}")

        fig, axs = plt.subplots(ncols=1, nrows=3, sharex='col')
        plt.subplots_adjust(hspace=0)
        
        axs[0].scatter(episodes, num_actions, s=1)
        axs[0].set_ylabel('Number of Actions')

        axs[1].scatter(episodes, total_reward, s=1)
        axs[1].set_ylabel('Total Reward')

        axs[2].scatter(episodes, crash_flag, s=1)
        axs[2].set_ylabel('End game state')

        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MONTE CARLO TRON - Learning using Monte Carlo on-policy")
    parser.add_argument('--players', '-p', type=int, help="Number of players - default 2", default=2)
    parser.add_argument('--size', '-s', type=int, help="Size of game grid - default 25", default=25)
    parser.add_argument('--vision_grid', '-v', type=int, help="Size of vision grid - default 3. Must be odd", default=3)
    parser.add_argument('--num_episodes', '-n', type=int, default=1000, help="Number of episodes - default 1000")
    parser.add_argument('--discount_rate', '-d', type=float, default=0.9, help="Discount rate for future rewards - default 0.9")
    parser.add_argument('--epsilon', '-e', type=float, default=0.2, help="Epsilon for greedy action selection - default 0.2")
    parser.add_argument('--filename_root', '-f', type=str, default=None, help="Filename root for saving - default None")
    parser.add_argument('--learning_rate', '-l', type=float, default=0.4, help="Learning rate - default 0.4")
    parser.add_argument('agents', nargs="*", default=['agent.wallhugger'], help="Opponent modules - default agent.wallhugger")
    args = parser.parse_args()

    if not args.vision_grid % 2:
        print("Vision grid not odd. Setting to 3")
        args.vision_grid = 3

    rl_agent = QLearning(players=args.players, size=args.size, agents=args.agents,
                          vision_grid_size=args.vision_grid, 
                          discount_rate=args.discount_rate, epsilon=args.epsilon,
                          filename_root=args.filename_root, learning_rate=args.learning_rate)
    rl_agent.run_simulation(num_episodes=args.num_episodes)
    rl_agent.visualize_learning()
