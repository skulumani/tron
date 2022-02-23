"""Replay interface to replay saved games using pygame"""
import numpy as np
import pygame
import argparse

import tron

class ReplayInterface():
    
    def __init__(self, width=800, fps=3):
        pygame.init()

        self.WIDTH=width
        self.FPS = fps

    def load(self, filename):
        """Load JSON game datafilename"""
        
        pass

    def _reset(self):

        rows = 10 
        cols = 10
        self.running = True
        self.cellsize = self.WIDTH // rows
        self.HEIGHT = cols * self.cellsize


        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('TRON REPLAY')
        self.clock = pygame.time.Clock()
    
    def _build_board(self):
        pass

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
    def update(self):
        pass

    def render(self):
        pass
    def _quit(self):
        pygame.quit()

    def run(self):
        while self.running:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(3)

        self.quit()


# load a game from command line argument
# determine total number of steps
# keyboard right will increment step counter
# render all steps from 0 to counter
# left keyboard goes down in step counter
# contiuous keypress capable
if __name__ == "__main__":
    replay = ReplayInterface()
    replay.run()

