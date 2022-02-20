import numpy as np
import enum 


class Status(enum.IntEnum):
    VALID = 0
    CRASH_INTO_WALL = 1
    CRASH_INTO_TAIL = 2
    CRASH_INTO_OPPONENT = 2
    CRASH_INTO_SELF = 3

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
    LEFT_45 = -1
    STRAIGHT = 0
    RIGHT_45 = 1
    RIGHT_90 = 2

# TODO add a mapping from (x,y) to numpy grid location
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
             (-1, -1)] # NW
    
    NORTH_FACING = [7, 1, 0]
    SOUTH_FACING = [3, 4, 5]
    EAST_FACING = [1, 2, 3]
    WEST_FACING = [5,6,7]

    ORIENTATION = [NORTH_FACING,
                   EAST_FACING,
                   SOUTH_FACING,
                   WEST_FACING]

    def __init__(self, y, x, orientation):
        """Constructor

        Args:
            y (int): Y coordinate of player in grid (row)
            x (int): X coordinate of player in grid (col)
            orientation (intEnum): orientation of player 0 <= orientation <= 7
        """

        self.x = x
        self.y = y
        self.orientation = Orientation(orientation)
        
        # save state history
        self.states = [{'y': self.y, 'x': self.x, 'orientation': self.orientation}]

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

        self.orientation = Orientation((self.orientation + action) % 8)
        dy, dx = Player.STEPS[self.orientation]
        
        self.x += dx
        self.y += dy

        self.states.append({'x': self.x, 'y': self.y, 'orientation': self.orientation})

    def front_crash(self, opponent):
        """Check if player crashes into opponents head

        Args: 
            opponent (Player): other player

        Returns:
            crash (bool): Logical crash if heads collide
        """

        crash = self.x == opponent.x and self.y == opponent.y
        return crash

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
        # self.players = self._init_players()
        self.players = self._init_two_players()

        self._update()
        observation = self._get_observation()
        return observation
   
    def _init_players(self):
        players = []
        
        wall_gap = 2
        rows = self.grid.shape[0]
        cols = self.grid.shape[1]
        # random locations for players on top/bottom
        x_location = np.random.choice(np.arange(0+wall_gap, cols+1-wall_gap), self.num_players)
        for x in x_location:
            y = np.random.choice([wall_gap, rows-1-wall_gap])
            orientation_options = Player.NORTH_FACING if y > self.halfsize else Player.SOUTH_FACING

            players.append(Player(y, x, np.random.choice(orientation_options)))

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
        for idx, player in enumerate(self.players):
            self.grid[player.y, player.x, idx+1] = 1

    def _get_observation(self):
        """Return representation of game

        Returns:
            observation (dict): Dictionary
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
            actions (List[int]): List of actions for each player
                -2: large CCW turn
                -1: small CCW turn
                 0: no turn - straight
                 1: small CW turn
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
        status = [Status.VALID for ii in range(self.num_players)]
        
        # players are valid - move them
        for player, action in zip(self.players, actions):
            player.act(action)

        # check if players have crashed into anything
        if self.num_players > 1:
            for idx, (player, opponent) in enumerate(zip(self.players, reversed(self.players))):
                status[idx] = self._validate_player(player, opponent)

        if sum(status) > 0:
            done = True

        if not done:
            self._update() # update each player

        observation = self._get_observation()
        return observation, done, status

    def _validate_player(self, player, opponent):
        """Check if player is in valid state

        Args:
            player (Player): player instance

        Returns:
            status (int): status for the current player
                0: valid
                1: crash into wall
                2: crash into tail
        """
        status = 0

        # check for crash into wall
        status = self._validate_wall(player)

        if status > 0:
            return status

        # check crash into a tail
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
        if self.grid[player.y,player.x,0]:
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
        # TODO - logic to check if self tail or which opponent
        if np.sum(self.grid[:,:,1:], axis=2)[player.y, player.x] > 0:
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


if __name__ == "__main__":
    tron = Tron(size=10, num_players=1)



        
         






