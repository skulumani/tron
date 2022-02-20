import numpy as np
import pygame

import tron

COLORS = {key:value[0:3] for key, value in pygame.colordict.THECOLORS.items()}
COLOR_PAIRS =  [(COLORS['blue4'], COLORS['blue1']),
                (COLORS['red4'], COLORS['red1']),
                (COLORS['darkorange4'], COLORS['darkorange1']),
                (COLORS['darkorchid4'], COLORS['darkorchid1']),
                (COLORS['aquamarine4'],COLORS['aquamarine1']),
                (COLORS['brown4'], COLORS['brown1']),
                (COLORS['cadetblue4'], COLORS['cadetblue1']),
                (COLORS['chartreuse4'], COLORS['chartreuse1']),
                (COLORS['coral4'], COLORS['coral1']),
                (COLORS['cyan4'], COLORS['cyan1']),
                (COLORS['darkgoldenrod4'], COLORS['darkgoldenrod1'])]
class Text():

    def __init__(self,size=16):
        self.font = pygame.font.Font(pygame.font.get_default_font(), size)

    def draw(self, string, color=COLORS['red'], background=COLORS['black']):
        return self.font.render(string, True, color, background)

class UserInterface():

    def __init__(self):

        # instantiate the game
        # TODO - define colors for the total number of players in game - dark variants for head
        self.game = tron.Tron(size=100, num_players=2)
        observation = self.game.reset()
        self.running = True

        # player colors
        num_players = self.game.num_players
        if num_players <= 2:
            self.player_colors = [{'head': COLOR_PAIRS[c][0], 'tail': COLOR_PAIRS[c][1]} for c in range(0, num_players)]
        elif num_players <= len(COLOR_PAIRS):    
            self.player_colors = [{'head': COLOR_PAIRS[c][0], 'tail': COLOR_PAIRS[c][1]} for c in np.random.choice(np.arange(0,len(COLOR_PAIRS)), num_players)]
        else:
            self.player_colors = [{'head': COLORS[c[0]], 'tail':COLORS[c[1]]} for c in np.random.choice(list(COLORS), (num_players, 2))]
    
        board = observation['board']
        rows = observation['board'].shape[0]
        cols = observation['board'].shape[1]

        self.WIDTH = 800 
        self.cellsize = self.WIDTH // rows
        self.HEIGHT = cols * self.cellsize
        
        pygame.init()
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('Tron')
        self.clock = pygame.time.Clock()

        # intialize image array and surface
        self.image = np.zeros((rows, cols, 3))
        self.image.fill(255) # everything white
        # build obstacles - only once
        self.image[board[:,:,0] == 1] = COLORS['black']
        self.surf = pygame.Surface((self.image.shape[0], self.image.shape[1]))
        self.scaled_surf = pygame.Surface((self.WIDTH, self.HEIGHT))

        # text object
        self.position_text = Text(size=16)

    def _reset(self):
        """Intialize everything"""
        pass
    def _build_board(self, observation):
        """Turn current game state into surface for pygame"""

        board = observation['board']
        positions = observation['positions']
        # draw tails
        for idx, color_dict in enumerate(self.player_colors):
            self.image[board[:, :, idx+1] == 1] = color_dict['tail']
        
        # draw heads
        for p, color_dict in zip(positions, self.player_colors):
            # import pdb;pdb.set_trace()
            self.image[p[0],p[1],:] = color_dict['head']

        # build surface
        pygame.surfarray.blit_array(self.surf, self.image.swapaxes(0, 1))

    def _draw_grid(self, surf):
        """Draw a grid onto the larger surface"""
        
        if self.cellsize >= 8:
            # vertical lines
            for r in range(self.image.shape[0]):
                pygame.draw.line(surf, COLORS['gray'], (r*self.cellsize,0), (r*self.cellsize, self.WIDTH))

            # horizontal
            for c in range(self.image.shape[1]):
                pygame.draw.line(surf, COLORS['gray'], (0, c*self.cellsize), (self.HEIGHT, c*self.cellsize))

        return surf

    def process_input(self):
        action = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key in (pygame.K_RIGHT,):
                    action = tron.Turn.RIGHT_90
                elif event.key in (pygame.K_LEFT,):
                    action = tron.Turn.LEFT_90
                elif event.key in (pygame.K_UP,):
                    action = tron.Turn.STRAIGHT
                elif event.key in (pygame.K_r,):
                    # reset game
                    self.game.reset()
                    self.done = False

        # get a user action (or from an agent) 
        return action

    def update(self, *action):
        # change game state
        # import pdb;pdb.set_trace()
        observation, done, status = self.game.move(*action)
        return observation, done, status

    def render(self, observation, string):
        # draw surface
        self._build_board(observation)

        pygame.transform.scale(self.surf, (self.WIDTH, self.HEIGHT), self.scaled_surf)
        self.scaled_surf = self._draw_grid(self.scaled_surf)

        # add text
        self.scaled_surf.blit(self.position_text.draw(string), (0,0))

        # self.window.fill(UserInterface.COLORS['white'])
        self.window.blit(self.scaled_surf, (0, 0))
        pygame.display.update()

    def run(self):
        """Game loop"""
        self.done = False
        while self.running:
            action = self.process_input()
            if action is not None and not self.done:
                observation, self.done, status = self.update(action, action)
                self.render(observation, "END" if self.done else "")
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    ui = UserInterface()
    ui.run()
