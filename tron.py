import numpy as np
import enum 
from itertools import combinations, permutations, product
from datetime import datetime
import json
from typing import Any, Optional

import numpy as np

import utilities

# type aliases
Location = tuple[int, int]  # location type (y, x)
PlayerState = dict[str, Any]
Observation = dict[str, Any]


class Status(enum.IntEnum):
    VALID = 0
    CRASH_INTO_WALL = 1
    CRASH_INTO_TAIL = 2
    CRASH_INTO_OPPONENT = 3
    CRASH_INTO_SELF = 4


class Orientation(enum.IntEnum):
    N = 0
    NE = 1
    E = 2
    SE = 3
    S = 4
    SW = 5
    W = 6
    NW = 7


class Turn(enum.IntEnum):
    LEFT_90 = -2
    # LEFT_45 = -1
    STRAIGHT = 0
    # RIGHT_45 = 1
    RIGHT_90 = 2


class Player:
    # movement possible - square grid - diagonals possible
    # (dy, dx)
    STEPS = [
        (-1, 0),  # N
        (-1, 1),  # NE
        (0, 1),  # E
        (1, 1),  # SE
        (1, 0),  # S
        (1, -1),  # SW
        (0, -1),  # W
        (-1, -1),  # NW
    ]

    NORTH_FACING = [0]
    SOUTH_FACING = [4]
    EAST_FACING = [2]
    WEST_FACING = [6]

    ORIENTATION = [NORTH_FACING, EAST_FACING, SOUTH_FACING, WEST_FACING]

    def __init__(self, y, x, orientation, uid=1, status=Status.VALID):
        """Constructor

        Args:
            y (int): Y coordinate of player in grid (row)
            x (int): X coordinate of player in grid (col)
            orientation (intEnum): orientation of player 0 <= orientation <= 7
        """

        self.uid = uid
        self.x = x
        self.y = y
        self.orientation = Orientation(orientation)
        self.status = status

        # save state history
        # state at each time step - location/postion, orientaiton, uid, status, action
        self.states: Optional[dict[str, any]] = {
            "y": [
                self.y,
            ],
            "x": [
                self.x,
            ],
            "orientation": [
                self.orientation,
            ],
            "uid": self.uid,
            "status": [
                self.status,
            ],
            "actions": [],
            "rewards": [],
            "location": [
                (self.y, self.x),
            ],
        }

    def act(self, action):
        """Rotate and move 1 unit forward

        Args:
            action (int): -2 <= action <= 2
                -2: large CCW turn
                -1: small CCW turn
                 0: no turn - straight
                 1: small CW turn
                 2: big CW turn
        """
        (y_new, x_new, orientation_new) = Player.future_move(
            self.y, self.x, self.orientation, action
        )
        self.y = y_new
        self.x = x_new
        self.orientation = orientation_new

        self.states["y"].append(self.y)
        self.states["x"].append(self.x)
        self.states["orientation"].append(self.orientation)
        self.states["actions"].append(action)

    @staticmethod
    def future_move(y, x, orientation, action) -> tuple[int, int, Orientation]:
        """Return the future position after performing a given action"""
        orientation = Orientation((orientation + action) % len(Orientation))
        dy, dx = Player.STEPS[orientation]

        x += dx
        y += dy
        return (y, x, orientation)

    def front_crash(self, opponent):
        """Check if player crashes into opponents head

        Args:
            opponent (Player): other player

        Returns:
            crash (bool): Logical crash if heads collide
        """

        crash = self.x == opponent.x and self.y == opponent.y
        if crash:
            return Status.CRASH_INTO_OPPONENT
        else:
            return Status.VALID

    def update_status(self, status: Status, reward: float):
        """Update player status and last state trajectory

        Args:
            status (Status): status of player

        """

        self.status = status
        self.states["status"].append(self.status)
        self.states["rewards"].append(reward)

        # TODO check if this is necessary
        self.states["status"][-1] = self.status


class Tron:
    """Define game board and collisions"""

    def __init__(self, size: int = 10, num_players: int = 2):
        """Default constructor

        Args:
            size (int): size of side of square grid for game
            num_players (int): number of players
        """

        self.size = size
        self.halfsize = size // 2
        self.num_players = num_players

    def reset(self) -> Observation:
        """Initialize game field and randomly place players

        Returns:
            observation (dict): from _get_observation - view of game
        """
        self.grid = self._define_grid()

        # initialize all the players
        self.players = self._init_players()
        # self.players = self._init_two_players()

        self._update()
        observation = self._get_observation()
        return observation

    def _init_players(self) -> list[Player]:
        players = []

        wall_gap = self.size // 10
        rows = self.grid.shape[0]
        cols = self.grid.shape[1]
        # random locations for players on top/bottom
        x_location = np.random.choice(
            np.arange(1 + wall_gap, cols - wall_gap - 1),
            size=self.num_players,
            replace=False,
        )
        y_location = [1 + wall_gap, rows - 1 - wall_gap]
        for idx, x in enumerate(x_location):
            y = y_location[idx % 2]
            orientation_options = (
                Player.NORTH_FACING if y > self.halfsize else Player.SOUTH_FACING
            )

            players.append(
                Player(
                    int(y), int(x), np.random.choice(orientation_options), uid=idx + 1
                )
            )

        return players

    def _init_two_players(self) -> list[Player]:
        players = []
        players.append(Player(5, 5, Orientation.E))
        players.append(Player(75, 75, Orientation.W))
        self.num_players = 2
        return players

    def _define_grid(self) -> np.ndarray:
        """Define game board

        Returns:
            grid (ndarray): nxnxm array of walls and player positions
        """
        # grid (0, 0) is in top left corner
        # positive x - move to larger/higher columns (right)
        # positive y - move to higher/larger rows (down)
        # third axis for player state
        grid = np.zeros([self.size, self.size, 1 + self.num_players])

        # draw boundary walls
        grid[0, :, 0] = 1
        grid[-1, :, 0] = 1
        grid[:, 0, 0] = 1
        grid[:, -1, 0] = 1

        return grid

    def _update(self) -> None:
        """Define player positions in the grid

        Update game board with the current player positions
        """
        # TODO: only move players in valid state
        for idx, player in enumerate(self.players):
            self.grid[player.y, player.x, player.uid] = 1

    def _get_observation(self) -> Observation:
        """Return representation of game

        Returns:
            observation (dict): Current game state
                - board (np.array): nD array representing game board m x n x p
                    m: y coordinate - positive down
                    n: x coordinate - positive right
                    p: player locations
                - positions (list): tuple (y, x) of each player current coordinates
                - orientations (tuple): tuple of length num_players of each player orientation
        """
        observation = {
            "board": self.grid.copy(),
            "positions": tuple([(p.y, p.x) for p in self.players]),
            "orientations": tuple([p.orientation for p in self.players]),
        }
        # TODO add rewards here
        return observation

    # TODO Add other game representations
    def move(self, *actions) -> tuple[Observation, bool, list, list] :
        """Move all the players

        Args:
            actions (List[int]): List of actions for each player - Turn enumeration
                -2: large CCW turn
                 0: no turn - straight
                 2: big CW turn

        Returns:
            observation (dict): Same as _get_observation
            done (bool): True if 1 or all players have crashed
            status (List[int]): List of the status for each player
                0: player is valid location
                1: player crashed into wall
                2: player crashed into another tail
        """
        done = False
        status = [p.status for p in self.players]

        # move the valid players
        for player, action in zip(self.players, actions):
            if player.status == Status.VALID:
                player.act(action)

        # check against walls - only update if valid
        for idx, p in enumerate(self.players):
            if p.status == Status.VALID:
                status[idx] = self._validate_wall(p)

        # check each player against the walls/tails
        if self.num_players == 1:
            status[0] = (
                self._validate_tail(self.players[0])
                if status[0] == Status.VALID
                else status[0]
            )
        else:
            # check if players have crashed into others
            for idx, (p, o) in enumerate(permutations(self.players, r=2)):
                if (
                    p.status == Status.VALID and 
                    status[idx // (self.num_players - 1)] == Status.VALID
                ):
                    # TODO Need to check which o current p crashed into and save
                    # this will simply tell us we crashed into another player, but not which one
                    if status[idx // (self.num_players - 1)] is Status.VALID:
                        status[idx // (self.num_players - 1)] = self._validate_player(
                            p, o
                        )

        # update player status and last state based on the computed status
        reward = [self._reward(s) for s in status]
        for s, r, p in zip(status, reward, self.players):
            # TODO Compute reward for each player
            # status should stay the same since we don't move if not valid
            p.update_status(s,r)

        # TODO: Fix logic for ending game with n > 2 players
        # done only when single player is remaining - when not singleplayer
        status_array = np.array(status)
        if self.num_players == 1:
            done = True if status[0] > Status.VALID else False
        elif len(status_array[status_array == 0]) == 1 and self.num_players > 1:
            done = True

        if not done:
            self._update()  # update game board

        observation = self._get_observation()
        return observation, done, status, reward
    
    def _reward(self, status: Status) -> float:
        """Return a reward based on a given status flag"""
        if status == Status.VALID:
            return 1
        elif status in (Status.CRASH_INTO_OPPONENT, Status.CRASH_INTO_SELF, Status.CRASH_INTO_TAIL, Status.CRASH_INTO_WALL):
            return -100

    def _validate_player(self, player: Player, opponent: Player) -> Status:
        """Check if player is in valid state

        Args:
            player (Player): player instance
            opponent (Player): opponent to check for a head on collision

        Returns:
            status (int): status for the current player
                0: valid
                1: crash into wall
                2: crash into tail
        """
        status = Status.VALID

        # check crash into any tails
        status = self._validate_tail(player)

        if status > 0:
            return status

        # check for crash into head
        status = player.front_crash(opponent)

        return status

    def _validate_wall(self, player: Player) -> Status:
        """Check if player crashes into a wall boundary

        Args:
            player (Player): player instance

        Returns:
            status (int): status for the player
                0: valid
                1: crash into wall
        """
        # check if outside game board
        rows, cols = self.grid.shape[0], self.grid.shape[1]
        if (
            player.y >= rows or player.x >= cols or player.y <= 0 or player.x <= 0
        ):  # exterior wall
            return Status.CRASH_INTO_WALL
        elif self.grid[player.y, player.x, 0]:  # obstacles in map
            return Status.CRASH_INTO_WALL
        else:
            return Status.VALID

    def _validate_tail(self, player: Player) -> Status:
        """Check if player crashed into a tail

        Args:
            player (Player): player instance

        Returns:
            status (int): status for the player
                0: player is valid
                2: player crashed into a tail
        """
        all_opponents = np.array([p.uid for p in self.players])
        all_opponents = all_opponents[all_opponents != player.uid]
        if self.grid[player.y, player.x, player.uid] > 0:
            return Status.CRASH_INTO_SELF
        elif np.sum(self.grid[player.y, player.x, all_opponents]) > 0:
            return Status.CRASH_INTO_TAIL
        else:
            return Status.VALID

    def _validate_front_crash(self, player1: Player, player2: Player) -> Status:
        """Check if two players heads have collided

        Args:
            player1 (Player): player 1 instance
            player2 (Player): player 2 instance

        Returns:
            status (int): status for player1
                0: valid
                2: crash into player2
        """
        if player1.front_crash(player2):
            return Status.CRASH_INTO_OPPONENT
        else:
            return Status.VALID

    @staticmethod
    def validate_position(yn: int, xn: int, board: np.ndarray) -> bool:
        """Check if potential position is occupied or not"""
        rows, cols = board.shape[0], board.shape[1]
        if yn >= rows or xn >= cols or yn <= 0 or xn <= 0:
            return False
        else:
            return False if np.sum(board[yn, xn, :]) > 0 else True

    def get_vision_grid(self, uid: int = 1, size: int = 3):
        """Return vision grid for current game state

        """
        # get current player position
        (y, x) = (self.players[uid-1].y, self.players[uid-1].x)
        rows = np.arange(y-size//2, y+size//2)
        cols = np.arange(x-size//2, x+size//2)
        
        # obstacle grid centered around current position
        obstacle_grid = np.zeros((size, size))
        player_grid = np.zeros((size, size))
        
        # TODO handle multiple opponents
        opponent_grid = np.zeros((size, size)) 

        for idx, r, c in enumerate(product(rows, cols)):
            # only extract values that lie within the grid (non negative or > grid_size)
            if r < 0 or c < 0 or r >= self.grid_size or c >= self.grid_size:
                continue
            obstacle_grids[idx] = self.grid[r, c, :]
            player_grid[idx] = self.grid[r, c, uid]
            opponent_grid[idx] = self.grid[r, c, uid+1]

        return obstacle_grid.flatten()

    def save(self, start_time: datetime = datetime.now()) -> str:
        """Save the game history to file

        Args:
            start_time (datetime): Time to append to the filename - defaults to now()
        """
        # TODO ensure saving and loading are working - write a unit test
        filename = "{}_tron.json".format(start_time.strftime("%Y%m%d-%H%M%S"))
        with open(filename, "w") as file:
            json.dump(
                {"grid": self.grid, "states": [p.states for p in self.players]},
                file,
                indent=4,
                cls=utilities.NumpyEncoder,
            )

        return filename

    @staticmethod
    def load(filename: str) -> tuple[np.ndarray, list]:
        """Load a game

        Args:
            filename (str): name of json file to load

        Returns:
            grid (np.array): Game board
            states (list): list of player states. Each is a list for the game with dict elements
                x: x position
                y: y position
                orientation: orientation from Orientation enum
                uid: player UID
                status: status falg from Status enum
        """
        with open(filename, "r") as file:
            data = json.load(file)

        # break out into useful variables
        return np.array(data["grid"]), data["states"]


if __name__ == "__main__":
    tron = Tron(size=10, num_players=1)
