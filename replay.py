"""Replay interface to replay saved games using pygame"""
import numpy as np
import pygame
import argparse

import tron
import interface

class ReplayInterface():
    
    def __init__(self, width=800, fps=3):
        pygame.init()

        self.WIDTH=width
        self.FPS = fps

    def load(self, filename):
        """Load JSON game datafilename"""
        self.grid, self.states = tron.Tron.load(filename) 
        
        # get total number of time steps
        self.players = [p for p in self.states]
        self.num_players = len(self.players)

        # get number of players
        # assign some random colors for the players
        if self.num_players <= 2:
            self.player_colors = [{'head': interface.COLOR_PAIRS[c][0], 'tail': interface.COLOR_PAIRS[c][1]} for c in range(0, self.num_players)]
        elif self.num_players <= len(interface.COLOR_PAIRS):    
            self.player_colors = [{'head': interface.COLOR_PAIRS[c][0], 'tail': interface.COLOR_PAIRS[c][1]} for c in np.random.choice(np.arange(1,len(interface.COLOR_PAIRS)), size=self.num_players, replace=False)]
        else:
            self.player_colors = [{'head': interface.COLORS[c[0]], 'tail': interface.COLORS[c[1]]} for c in np.random.choice(list(interface.COLORS), size=(self.num_players, 2), replace=False)]

        # first player is always blue
        self.player_colors[0] = {'head': interface.COLOR_PAIRS[0][0], 'tail': interface.COLOR_PAIRS[0][1]}
        
        # get all the states extracted for the players
        self._reset()

    def _reset(self):

        self.step = 0 # step for trajectory plotting
        self.running = True
        self.rows = self.grid.shape[0]
        self.cols = self.grid.shape[1]
        self.cellsize = self.WIDTH // self.rows
        self.HEIGHT = self.cols * self.cellsize

        # intialize image array and surface
        self.image = np.zeros((self.rows, self.cols, 3))
        self.image.fill(255) # everything white
        # build obstacles
        self.image[self.grid[:,:,0] == 1] = interface.COLORS['black']

        self.surf = pygame.Surface((self.image.shape[0], self.image.shape[1]))
        self.scaled_surf = pygame.Surface((self.WIDTH, self.HEIGHT))
        # text object
        self.position_text = interface.Text(size=16)

        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('TRON REPLAY')
        self.clock = pygame.time.Clock()
    
    def _build_board(self):
        # set all white
        self.image.fill(255)
        # draw walls v
        self.image[self.grid[:,:,0] == 1] = interface.COLORS['black']

        # draw the players up through current step
        for idx, color_dict in enumerate(self.player_colors):
            x = [state['x'] for state in self.players[idx]]
            y = [state['y'] for state in self.players[idx]]
            status = [state['status'] for state in self.players[idx]]

            # make sure we don't go over max number of states
            max_step = self.step if self.step <= len(x) else len(x)
            self.image[y[0:max_step], x[0:max_step], :] = color_dict['tail']

        # build surface
        pygame.surfarray.blit_array(self.surf, self.image.swapaxes(0, 1))

    def _draw_grid(self, surf):
        pass
    
    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False
                    break
                if event.key in (pygame.K_RIGHT,):
                    self.step += 1
                if event.key in (pygame.K_LEFT,):
                    self.step -= 1
                if event.key in (pygame.K_r,):
                    self._reset()

    def update(self):
        pass

    def _draw_grid(self, surf):
        """Draw a grid onto the larger surface"""
        
        if self.cellsize >= 8:
            # vertical lines
            for r in range(self.image.shape[0]):
                pygame.draw.line(surf, interface.COLORS['gray'], (r*self.cellsize,0), (r*self.cellsize, self.WIDTH))

            # horizontal
            for c in range(self.image.shape[1]):
                pygame.draw.line(surf, interface.COLORS['gray'], (0, c*self.cellsize), (self.HEIGHT, c*self.cellsize))

        return surf

    def render(self):
        # draw surface
        self._build_board()

        pygame.transform.scale(self.surf, (self.WIDTH, self.HEIGHT), self.scaled_surf)
        self.scaled_surf = self._draw_grid(self.scaled_surf)

        # add text
        self.scaled_surf.blit(self.position_text.draw("Step: {}".format(self.step)), (0,0))

        self.window.blit(self.scaled_surf, (0, 0))
        pygame.display.update()

    def _quit(self):
        pygame.quit()

    def run(self):
        while self.running:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(3)

        self._quit()


# load a game from command line argument
# determine total number of steps
# keyboard right will increment step counter
# render all steps from 0 to counter
# left keyboard goes down in step counter
# contiuous keypress capable
if __name__ == "__main__":
    replay = ReplayInterface()
    replay.load('20220222-213143_tron.json')
    replay.run()

