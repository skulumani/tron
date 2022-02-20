import numpy as np
import pygame

import tron

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
        self.game = tron.Tron(size=100, num_players=2)
        observation = self.game.reset()
        self.done = False

        self.WIDTH = 800 
        self.cellsize = self.WIDTH // observation['board'].shape[0]
        self.HEIGHT = observation['board'].shape[1] * self.cellsize
        
        pygame.init()
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('Tron')
        self.clock = pygame.time.Clock()

        
    def _draw_board(self, observation):
        """Turn current game state into image array for pygame"""

        board = observation['board']
        image = np.zeros((self.game.size, self.game.size, 3))

        # draw obstacles
        image[board[:,:,0] != 1] = UserInterface.COLORS['white']

        # draw players
        for ii in range(1, board.shape[2]):
            image[board[:, :, ii] == 1] = UserInterface.COLORS['blue']
        
        # build surface
        surf = pygame.Surface((image.shape[0], image.shape[1]))
        pygame.surfarray.blit_array(surf, image)
        surf = pygame.transform.scale(surf, (self.WIDTH, self.HEIGHT))
        surf = self._draw_grid(surf, image)

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
                print(observation['board'][:, :, 1])
                self.render(observation)
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    ui = UserInterface()
    ui.run()
