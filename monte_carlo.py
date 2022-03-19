"""Monte Carlo learning for Tron"""
import argparse
import json
import os
from typing import Dict, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import tron

class MonteCarlo:

    def __init__(self, players: int = 2, size: int = 25, agents: str = 'agent.semideterministic'):
        pass

    def run_simulation(self):
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MONTE CARLO TRON - Learning using Monte Carlo on-policy")
    parser.add_argument('--players', '-p', type=int, help="Number of players - default 2", default=2)
    parser.add_argument('--size', '-s', type=int, help="Size of grid - default 25", default=25)
    parser.ad_argument('agents', nargs="*", default=['agent.semideterministic'], help="Opponent modules, e.g. agent.dumb")
    args = parser.parse_args()

    rl_agent = MonteCarlo(players=args.players, size=args.size, agents=args.agents)
    rl_agent.run_simulation()
    rl_agent.visualize_learning()
