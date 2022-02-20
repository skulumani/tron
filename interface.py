import numpy as np
import pygame

import tron

class UserInterface():
    COLORS = {key:value[0:3] for key, value in pygame.colordict.THECOLORS.items()}

    def __init__(self):

        # instantiate the game
        self.game = tron.Tron(size=100, num_players=2)
        observation = self.game.reset()
        self.done = False
    
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
        self.image[board[:,:,0] == 1] = UserInterface.COLORS['black']
        self.surf = pygame.Surface((self.image.shape[0], self.image.shape[1]))
        self.scaled_surf = pygame.Surface((self.WIDTH, self.HEIGHT))

        # text object
        self.font = pygame.font.Font(pygame.font.get_default_font(), 32)
        self.text_surf = self.font.render("test", True, UserInterface.COLORS['red'])

    def _build_board(self, observation):
        """Turn current game state into image array for pygame"""

        board = observation['board']

        # draw players
        for ii in range(1, board.shape[2]):
            self.image[board[:, :, ii] == 1] = UserInterface.COLORS['blue']
        
        # build surface
        pygame.surfarray.blit_array(self.surf, self.image)

    def _draw_grid(self, surf):
        """Draw a grid onto the larger surface"""
        
        if self.cellsize >= 8:
            # vertical lines
            for r in range(self.image.shape[0]):
                pygame.draw.line(surf, UserInterface.COLORS['gray'], (r*self.cellsize,0), (r*self.cellsize, self.WIDTH))

            # horizontal
            for c in range(self.image.shape[1]):
                pygame.draw.line(surf, UserInterface.COLORS['gray'], (0, c*self.cellsize), (self.HEIGHT, c*self.cellsize))

        return surf

    def _draw_text(self, surf, string):
        self.text_surf = self.font.render(string, True, UserInterface.COLORS['red'])
        surf.blit(self.text_surf,(0,0))
        return surf

    def process_input(self):
        action = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.done = True
                elif event.key in (pygame.K_RIGHT,):
                    action = tron.Turn.RIGHT_90
                elif event.key in (pygame.K_LEFT,):
                    action = tron.Turn.LEFT_90
                elif event.key in (pygame.K_UP,):
                    action = tron.Turn.STRAIGHT

        # get a user action (or from an agent) 
        return action

    def update(self, *action):
        # change game state
        # import pdb;pdb.set_trace()
        observation, done, status = self.game.move(*action)
        return observation, done, status

    def render(self, observation):
        # draw surface
        self._build_board(observation)

        self.scaled_surf = pygame.transform.scale(self.surf, (self.WIDTH, self.HEIGHT))
        self.scaled_surf = self._draw_grid(self.scaled_surf)
        self.scaled_surf = self._draw_text(self.scaled_surf, "P1: {}".format(observation['positions'][0]))

        # self.window.fill(UserInterface.COLORS['white'])
        self.window.blit(self.scaled_surf, (0, 0))
        pygame.display.update()

    def run(self):
        """Game loop"""
        while not self.done:
            action = self.process_input()
            if action is not None:
                observation, done, status = self.update(action, action)
                self.render(observation)
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    ui = UserInterface()
    ui.run()
