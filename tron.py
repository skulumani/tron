import numpy as np
import enum 


class Status(enum.Enum):
    VALID = enum.auto()
    CRASH_INTO_WALL = enum.auto()
    CRASH_INTO_OPPONENT = enum.auto()

class Player:
    # movement possible - square grid - diagonals possible
    # (dx, dy)
    STEPS = [(0, -1), # N 
             (1, -1), # NE
             (1, 0), # E
             (1, 1), # SE
             (0, 1), # S
             (-1, 1), # SW
             (-1, 0), # W
             (-1, -1)] # NW

    def __init__(self, x, y, orientation):
        """Constructor

        Args:
            x (int): X coordinate of player in grid
            y (int): Y coordinate of player in grid
            orientation (int): orientation of player 0 <= orientation <= 7
        """

        self.x = x
        self.y = y
        self.orientation = int(orientation)
        
        # save state history
        self.states = [{'x': self.x, 'y': self.y, 'orientation': self.orientation}]

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

        self.orientation = int((self.orientation + action) % 8)
        dx, dy = Player.STEPS[self.orientation]
        
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
        # grid (0, 0) is in bottom left corner 
        # positive x - move to larger/higher columns (right)
        # positive y - move to lower/smaller rows (up)
        self.grid = np.zeros([self.size, self.size, self.num_players]) # third axis for player state 
        
        # initialize all the players
        
        # random location near wall
        # random orientation away from the wall or always towards center
        # wall_gap = np.random.randint(0, 3) # distance from wall
        wall_gap = 1
        # wall_distance = np.random.choise(np.arange(2*self.size - 1), self.num_players) # distance along wall boundary

        # initialize only 2 players for now
        # player 1 - bottom wall
        # player 2 - top wall
        self.players = [
            Player(np.random.randint(0, self.size), self.size - 1 - wall_gap, np.random.choice([0, 1, 2, 6, 7])),
            Player(np.random.randint(0, self.size), wall_gap, np.random.choice([2, 3, 4, 5, 6]))]



