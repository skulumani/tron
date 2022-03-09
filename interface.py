import numpy as np
import pygame
import argparse
from datetime import datetime

import tron
from agent import dumb

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

    def __init__(self, size=100, num_players=2, width=800, human=True, 
                 record=False, fps=3):

        pygame.init()
        # TODO - define colors for the total number of players in game - dark variants for head
        self.size = size
        self.num_players = num_players
        self.WIDTH = width
        self.human = human # player 1 actions are human keyboard control
        self.FPS = fps
        self.RECORD = record

        # intialize game
        self._reset()


    def _reset(self):
        """Intialize everything"""
        self.game = tron.Tron(self.size, self.num_players)
        self.observation = self.game.reset()

        self.running = True
        self.done = False

        # player colors
        if self.num_players <= 2:
            self.player_colors = [{'head': COLOR_PAIRS[c][0], 'tail': COLOR_PAIRS[c][1]} for c in range(0, self.num_players)]
        elif self.num_players <= len(COLOR_PAIRS):    
            self.player_colors = [{'head': COLOR_PAIRS[c][0], 'tail': COLOR_PAIRS[c][1]} for c in np.random.choice(np.arange(1,len(COLOR_PAIRS)), size=self.num_players, replace=False)]
        else:
            self.player_colors = [{'head': COLORS[c[0]], 'tail':COLORS[c[1]]} for c in np.random.choice(list(COLORS), size=(self.num_players, 2), replace=False)]

        # first player is always blue
        self.player_colors[0] = {'head': COLOR_PAIRS[0][0], 'tail': COLOR_PAIRS[0][1]}
    
        board = self.observation['board']
        rows = self.observation['board'].shape[0]
        cols = self.observation['board'].shape[1]

        self.cellsize = self.WIDTH // rows
        self.HEIGHT = cols * self.cellsize

        # intialize image array and surface
        self.image = np.zeros((rows, cols, 3))
        self.image.fill(255) # everything white
        # build obstacles
        self.image[board[:,:,0] == 1] = COLORS['black']
        self.surf = pygame.Surface((self.image.shape[0], self.image.shape[1]))
        self.scaled_surf = pygame.Surface((self.WIDTH, self.HEIGHT))
        # text object
        self.position_text = Text(size=16)

        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('Tron')
        self.clock = pygame.time.Clock()


    def _build_board(self, observation):
        """Turn current game state into surface for pygame"""

        board = observation['board']
        positions = observation['positions']
        orientations = observation['orientations']
        
        # set all white
        self.image.fill(255)

        # draw walls v
        self.image[board[:,:,0] == 1] = COLORS['black']

        # draw tails
        for idx, color_dict in enumerate(self.player_colors):
            self.image[board[:, :, idx+1] == 1] = color_dict['tail']

        # draw heads
        for p, o, color_dict in zip(positions, orientations, self.player_colors):
            self.image[p[0],p[1],:] = color_dict['head']
            # # draw possible steps
            # # iterate through Steps[turns + current orientation]
            # for t in tron.Turn:
            #     # get future square and color
            #     (y, x, orientation) = tron.Player.future_move(p[0], p[1], o, t)
            #     # don't draw if any point outside grid
            #     if y < self.image.shape[0] and x < self.image.shape[1] and y >= 0 and x >= 0:
            #         self.image[y,x,:] = COLORS['lightyellow1']

        
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
        actions = []
        action = None
        # TODO Allow for continous key presses
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False
                elif event.key in (pygame.K_RIGHT,):
                    action = tron.Turn.RIGHT_90
                elif event.key in (pygame.K_LEFT,):
                    action = tron.Turn.LEFT_90
                elif event.key in (pygame.K_UP,):
                    action = tron.Turn.STRAIGHT
                elif event.key in (pygame.K_r,):
                    # reset game
                    self._reset()
                elif event.key in (pygame.K_s,):
                    self.game.save()
                elif event.key in (pygame.K_p,):
                    # print states of each player
                    print(self.game.players[0].states)
                    

        # first action is human - rest are AI
        # TODO - generalize to allow user functional input for agent
        if self.human is True and action is not None:
            actions.append(action)
            for idx in range(1, self.num_players):
                actions.append(dumb.generate_move(self.observation['board'],
                                                        self.observation['positions'],
                                                        self.observation['orientations']))
        elif self.human is False: # all AI players
            actions = [dumb.generate_move(self.observation['board'],
                                                self.observation['positions'],
                                                self.observation['orientations']) for ii in range(self.num_players)]
        return actions


    def update(self, *action):
        # change game state
        self.observation, self.done, self.status = self.game.move(*action)

    def render(self, string):
        # draw surface
        self._build_board(self.observation)

        pygame.transform.scale(self.surf, (self.WIDTH, self.HEIGHT), self.scaled_surf)
        self.scaled_surf = self._draw_grid(self.scaled_surf)

        # add text
        self.scaled_surf.blit(self.position_text.draw(string), (0,0))

        # self.window.fill(UserInterface.COLORS['white'])
        self.window.blit(self.scaled_surf, (0, 0))
        pygame.display.update()

    
    def _quit(self):
        """Close and quit"""
        pygame.quit()

    def run(self):
        """Game loop"""
        while self.running:
            actions = self.process_input()
            if actions and not self.done:
                self.update(*actions)
            # TODO Use status to determine winner - only single player with valid status
            self.render("".join(["P{}:{} ".format(idx,s) for idx,s in enumerate(self.status)]) if self.done else "")
            self.clock.tick(self.FPS)
        
        self._quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TRON UI - Run single games against the AI or fully autonomously. Keyboard arrows, s to save, r to reset, esc to quit. ')
    parser.add_argument('--players', '-p', type=int, help="Number of players", default=2)
    parser.add_argument('--size', '-s', type=int, help="Size of grid", default=100)
    parser.add_argument('--interactive', '-i', action='store_true', help="Player 1 is human. If not set then all will be using the same agent.")
    # parser.add_argument('--record', '-r', action='store_true', help='Record the visualization')
    parser.add_argument('--fps', '-f', type=int, default=5, help='Change FPS.')

    # TODO add parsing for the AI agent to use for the AI

    # TODO validate number of agents = players - human players
    args = parser.parse_args()
    ui = UserInterface(size=args.size, num_players=args.players, 
                       human=args.interactive, fps=args.fps)
    ui.run()
