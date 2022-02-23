import numpy as np
import enum 
from itertools import combinations, permutations
from datetime import datetime
import json

import utilities


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
    STEPS = [(-1, 0), # N 
             (-1, 1), # NE
             (0, 1), # E
             (1, 1), # SE
             (1, 0), # S
             (1, -1), # SW
             (0, -1), # W
             (-1, -1) # NW
             ]
    
    NORTH_FACING = [0]
    SOUTH_FACING = [4]
    EAST_FACING = [2]
    WEST_FACING = [6]

    ORIENTATION = [NORTH_FACING,
                   EAST_FACING,
                   SOUTH_FACING,
                   WEST_FACING]

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
        self.states = [{'y': self.y, 'x': self.x, 'orientation': self.orientation, 'uid': self.uid, 'status':self.status}]

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
        (self.y, self.x, self.orientation) = Player.future_move(self.y, self.x, self.orientation,action)
        self.states.append(self.state())
   
    @staticmethod
    def future_move(y, x, orientation, action):
        orientation = Orientation((orientation + action) % len(Orientation))
        dy, dx = Player.STEPS[orientation]
        
        x += dx
        y += dy
        return (y,x,orientation)

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

    def state(self):
        """Return state as tuple"""
        return {'y': self.y, 'x': self.x, 'orientation': self.orientation, 'uid': self.uid, 'status': self.status}

    def update_status(self, status):
        """Update player status and last state trajectory

        Args:
            status (Status): status of player

        """
        self.status = status
        self.states[-1]['status'] = self.status

class Tron:
    """Define game board and collisions"""

    def __init__(self, size=10, num_players=2):
        """Default constructor

        Args:
            size (int): size of side of square grid for game
            num_players (int): number of players
        """

        self.size = size
        self.halfsize = size // 2
        self.num_players = num_players

    def reset(self):
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
   
    def _init_players(self):
        players = []
        
        wall_gap = self.size // 10
        rows = self.grid.shape[0]
        cols = self.grid.shape[1]
        # random locations for players on top/bottom
        x_location = np.random.choice(np.arange(1+wall_gap, cols-wall_gap-1), size=self.num_players, replace=False)
        y_location = [1+wall_gap, rows-1-wall_gap]
        for idx,x in enumerate(x_location):
            y = y_location[idx % 2]
            orientation_options = Player.NORTH_FACING if y > self.halfsize else Player.SOUTH_FACING

            players.append(Player(int(y), int(x), np.random.choice(orientation_options), uid=idx+1))

        return players

    def _init_two_players(self):
        players = []
        players.append(Player(5, 5, Orientation.E))
        players.append(Player(75,75, Orientation.W))
        self.num_players = 2
        return players

    def _define_grid(self):
        """Define game board
        
        Returns:
            grid (ndarray): nxnxm array of walls and player positions
        """
        # grid (0, 0) is in top left corner
        # positive x - move to larger/higher columns (right)
        # positive y - move to higher/larger rows (down)
        grid = np.zeros([self.size, self.size, 1+self.num_players]) # third axis for player state 
        # draw boundary walls
        grid[0,:,0] = 1
        grid[-1,:,0] = 1
        grid[:,0,0]=1
        grid[:,-1,0]=1

        return grid

    def _update(self):
        """Define player positions in the grid"""
        # TODO: only move players in valid state
        for idx, player in enumerate(self.players):
            self.grid[player.y, player.x, player.uid] = 1

    def _get_observation(self):
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
            'board': self.grid.copy(),
            'positions': tuple([(p.y, p.x) for p in self.players]),
            'orientations': tuple([p.orientation for p in self.players])}
        return observation

    def move(self, *actions):
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
        for idx,p in enumerate(self.players):
            if p.status == Status.VALID:
                status[idx] = self._validate_wall(p)

        # check each player against the walls/tails
        if self.num_players == 1:
            status[0] = self._validate_tail(self.players[0]) if status[0] == Status.VALID else status[0]
        else:
            # check if players have crashed into others
            for idx, (p, o) in enumerate(permutations(self.players, r=2)):
                if p.status == Status.VALID and status[idx//(self.num_players-1)] == Status.VALID:
                    # TODO Need to check which o current p crashed into and save
                    # this will simply tell us we crashed into another player, but not which one
                    if status[idx//(self.num_players-1)] is Status.VALID:
                        status[idx//(self.num_players-1)] = self._validate_player(p, o)
        
        # update player status and last state based on the computed status
        for s,p in zip(status, self.players):
            if p.status is Status.VALID:
                p.update_status(s)

        # TODO: Fix logic for ending game with n > 2 players
        # done only when single player is remaining - when not singleplayer
        status_array = np.array(status)
        if self.num_players == 1:
            done = True if status[0] > Status.VALID else False
        elif len(status_array[status_array == 0]) == 1 and self.num_players > 1:
            done = True

        if not done:
            self._update() # update game board
        
        observation = self._get_observation()
        return observation, done, status

    def _validate_player(self, player, opponent):
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

    def _validate_wall(self, player):
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
        if player.y >= rows or player.x >= cols or player.y <= 0 or player.x <= 0: # exterior wall
            return Status.CRASH_INTO_WALL
        elif self.grid[player.y,player.x,0]: # obstacles in map
            return Status.CRASH_INTO_WALL
        else:
            return Status.VALID

    def _validate_tail(self, player):
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
        if self.grid[player.y,player.x,player.uid] > 0:
            return Status.CRASH_INTO_SELF
        elif np.sum(self.grid[player.y, player.x, all_opponents]) > 0:
            return Status.CRASH_INTO_TAIL
        else:
            return Status.VALID

    def _validate_front_crash(self, player1, player2):
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
            Status.CRASH_INTO_OPPONENT
        else:
            Status.VALID

    def save(self, start_time=datetime.now()):
        """Save the game history to file
        
        Args:
            start_time (datetime): Time to append to the filename - defaults to now()
        """
        filename = "{}_tron.json".format(start_time.strftime("%Y%m%d-%H%M%S"))
        with open(filename, 'w') as file:
            json.dump({'grid': self.grid,
                       'states': [p.states for p in self.players]}, file, indent=4, cls=utilities.NumpyEncoder) 

        return filename

    @staticmethod
    def load(filename):
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
        with open(filename, 'r') as file:
            data = json.load(file)

        # break out into useful variables
        return np.array(data['grid']), data['states']

if __name__ == "__main__":
    tron = Tron(size=10, num_players=1)



        
         






