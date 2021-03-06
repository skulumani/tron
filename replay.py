"""Replay interface to replay saved games using pygame"""
import numpy as np
import pygame
import argparse

import tron
import interface

class ReplayInterface():
    
    def __init__(self, width=800, fps=30):
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
        # for idx, p for enumerate(self.players):
        #     x = [state['x'] for state in p]
        #     y = [state['y'] for state in p]
        #     orientation = [state['orientation'] for state in p]
        #     status = [state['status'] for state in p]
        #     uid = [state['uid'] for state in p]
            
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
            x = self.players[idx]['x']
            y = self.players[idx]['y']
            status = self.players[idx]['status']
            rewards = self.players[idx]['rewards']

            # make sure we don't go over max number of states
            max_step = self.step if self.step <= len(x) else len(x)
            head_idx = 0 if max_step == 0 else max_step-1
            self.image[y[0:max_step], x[0:max_step], :] = color_dict['tail']
            self.image[y[head_idx], x[head_idx], :] = color_dict['head']

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
                elif event.key in (pygame.K_RIGHT,):
                    self.step += 1
                elif event.key in (pygame.K_LEFT,):
                    self.step -= 1
                elif event.key in (pygame.K_r,):
                    self._reset()

        keys = pygame.key.get_pressed()
        self.step += keys[pygame.K_l] - keys[pygame.K_h]

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

        # add current status flag for every player
        status = []
        for p in self.players:
            idx = self.step if self.step < len(p['status']) else (len(p['status'])-1)
            status.append(tron.Status(p['status'][idx]))

        string = f"Step:{self.step}  "
        for idx, s in enumerate(status):
            string += f"P{idx}:{s.name} "

        self.scaled_surf.blit(self.position_text.draw(string), (0,0))

        self.window.blit(self.scaled_surf, (0, 0))
        pygame.display.update()

    def _quit(self):
        pygame.quit()

    def run(self):
        while self.running:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(self.FPS)

        self._quit()

# contiuous keypress capable
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TRON REPLAY - Replay games. Keyboard left/right to step, r reset, q/esc quit")
    parser.add_argument("save_game", nargs=1, help="Replay save file", type=str)
    args = parser.parse_args()

    replay = ReplayInterface()
    replay.load(args.save_game[0])
    replay.run()

