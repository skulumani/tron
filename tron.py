import numpy as np
import enum 
import pygame


class Status(enum.Enum):
    VALID = enum.auto()
    CRASH_INTO_WALL = enum.auto()
    CRASH_INTO_OPPONENT = enum.auto()

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
    
    NORTH_FACING = [0, 1, 7]
    SOUTH_FACING = [3, 4, 5]
    EAST_FACING = [1, 2, 3]
    WEST_FACING = [7, 6, 5]

    ORIENTATION = [NORTH_FACING,
                   EAST_FACING,
                   SOUTH_FACING,
                   WEST_FACING]

    def __init__(self, y, x, orientation):
        """Constructor

        Args:
            y (int): Y coordinate of player in grid (row)
            x (int): X coordinate of player in grid (col)
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
        
        # random location near wall
        # random orientation away from the wall or always towards center
        # wall_gap = np.random.randint(0, 3) # distance from wall
        wall_gap = 1
        # wall_distance = np.random.choise(np.arange(2*self.size - 1), self.num_players) # distance along wall boundary

        # initialize half of players on top wall and other half on bottom
        # player 1 - bottom wall
        # player 2 - top wall
        self.players = [ ]
        x_location = np.random.choice(np.arange(self.size), self.num_players)
        for x in x_location:
            y = np.random.choice([self.size - 1 - wall_gap, wall_gap])
            orientation_options = Player.NORTH_FACING if y > self.halfsize else Player.SOUTH_FACING

            self.players.append(Player(y, x, np.random.choice(orientation_options)))

            # self.players = [
            #     Player(np.random.randint(0, self.size), self.size - 1 - wall_gap, np.random.choice([0, 1, 2, 6, 7])),
            #     Player(np.random.randint(0, self.size), wall_gap, np.random.choice([2, 3, 4, 5, 6]))]
        self._update()
        observation = self._get_observation()
        return observation
    
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
                - positions (tuple): tuple of each player current coordinates
                - orientations (tuple): tuple of each player orientation
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
        status = [0 for ii in range(self.num_players)]

        # players are valid - move them
        for player, action in zip(self.players, actions):
            player.act(action)

        # check if players have crashed
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
        horizontal_wall = player.y < 0 or player.y >= self.size
        vertical_wall = player.x < 0 or player.x >= self.size
        
        if horizontal_wall or vertical_wall:
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
        if np.sum(self.grid, axis=2)[player.y, player.x] > 0:
            return Status.CRASH_INTO_OPPONENT
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

class UserInterface():
    COLORS = {'black': (0, 0, 0),
              'red': (255, 0, 0),
              'blue': (0, 255, 0),
              'green': (0, 0, 255),
              'white': (255, 255, 255),
              'gray': (128, 128, 128)
              }

    def __init__(self):

        # instantiate the game
        self.game = Tron(size=100, num_players=2)
        self.observation = self.game.reset()
        self.done = False

        # get initial board
        self.board = self.observation['board']
        self.image = np.zeros((self.game.size, self.game.size, 3))
        self.image[self.board[:,:,0] != 1] = UserInterface.COLORS['white']

        self.WIDTH = 800 
        self.cellsize = self.WIDTH // self.image.shape[0]
        self.HEIGHT = self.image.shape[1] * self.cellsize

        pygame.init()
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('Tron')
        self.clock = pygame.time.Clock()

        # draw surface
        self.surf = pygame.Surface((self.image.shape[0], self.image.shape[1]))
        pygame.surfarray.blit_array(self.surf, self.image)
        self.surf = pygame.transform.scale(self.surf, (self.WIDTH, self.HEIGHT))
        self._draw_grid()

    def _draw_grid(self):
        """Draw a game grid between cells"""

        # vertical lines
        for r in range(self.image.shape[0]):
            pygame.draw.line(self.surf, UserInterface.COLORS['gray'], (r*self.cellsize,0), (r*self.cellsize, self.WIDTH))

        # horizontal
        for c in range(self.image.shape[1]):
            pygame.draw.line(self.surf, UserInterface.COLORS['gray'], (0, c*self.cellsize), (self.HEIGHT, c*self.cellsize))
            

    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.done = True

        # get a user action (or from an agent) 
    
    def update(self):
        # change game state

        # self.observation, self.done, self.status = self.game.act()
        pass

    def render(self):
        self.window.fill(UserInterface.COLORS['white'])
        self.window.blit(self.surf, (0, 0))
        pygame.display.update()

    def run(self):
        while not self.done:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    ui = UserInterface()
    ui.run()



        
         






