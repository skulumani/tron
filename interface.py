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
        # build obstacles
        self.image[board[:,:,0] == 1] = UserInterface.COLORS['black']
        
    def _draw_board(self, observation):
        """Turn current game state into image array for pygame"""

        board = observation['board']

        # draw players
        for ii in range(1, board.shape[2]):
            self.image[board[:, :, ii] == 1] = UserInterface.COLORS['blue']
        
        # build surface
        surf = pygame.Surface((self.image.shape[0], self.image.shape[1]))
        pygame.surfarray.blit_array(surf, self.image)
        surf = pygame.transform.scale(surf, (self.WIDTH, self.HEIGHT))
        surf = self._draw_grid(surf, self.image)

        return surf

    def _draw_grid(self, surf, image):
        """Draw a game grid between cells"""

        # vertical lines
        for r in range(image.shape[0]):
            pygame.draw.line(surf, UserInterface.COLORS['gray'], (r*self.cellsize,0), (r*self.cellsize, self.WIDTH))

        # horizontal
        for c in range(image.shape[1]):
            pygame.draw.line(surf, UserInterface.COLORS['gray'], (0, c*self.cellsize), (self.HEIGHT, c*self.cellsize))

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
        surf = self._draw_board(observation)
        self.window.fill(UserInterface.COLORS['white'])
        self.window.blit(surf, (0, 0))
        pygame.display.update()

    def run(self):
        while not self.done:
            action = self.process_input()
            if action is not None:
                print(action)
                observation, done, status = self.update(action, action)
                print(observation['positions'])
                self.render(observation)
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    ui = UserInterface()
    ui.run()
