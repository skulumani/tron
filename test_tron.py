import numpy as np
import pytest

import tron

class TestPlayer():
    def test_position(self):
        for ii in range(100):
            x = np.random.randint(0, 50)
            y = np.random.randint(50, 100)
            player = tron.Player(y, x, 1)
            np.testing.assert_equal([player.y, player.x], [y, x])

    def test_north_motion(self):
        x = np.random.randint(0, 50)
        y = np.random.randint(0, 50)
        orientation = tron.Orientation.N # north facing
        steps = [(0, -1), # W 
                 (-1, -1), # NW
                 (-1, 0), #N
                 (-1, 1), # NE
                 (0, 1)] # E

        for action, step in zip(list(tron.Turn), steps):
            player = tron.Player(y, x, orientation)
            player.act(action)
            dy, dx = step
            yd = y + dy
            xd = x + dx
            print("Start: ({}, {}) Act: {} End: ({}, {})".format(y, x, action.name,player.y, player.x))
            np.testing.assert_equal([player.y, player.x], [yd, xd])

    def test_north_east_motion(self):
        x = np.random.randint(0, 50)
        y = np.random.randint(0, 50)
        orientation = tron.Orientation.NE 
        steps = [(-1, -1), # NW 
                 (-1, 0), # N
                 (-1, 1), # NE
                 (0, 1), # E
                 (1, 1)] # SE

        for action, step in zip(list(tron.Turn), steps):
            player = tron.Player(y, x, orientation)
            player.act(action)
            dy, dx = step
            yd = y + dy
            xd = x + dx
            print("Start: ({}, {}) Act: {} End: ({}, {})".format(y, x, action.name,player.y, player.x))
            np.testing.assert_equal([player.y, player.x], [yd, xd])

    # TODO - test out each orientation with motion
    
    def test_front_crash_false(self):
        for ii in range(100):
            x = np.random.randint(0,100)
            y = np.random.randint(0, 100)
            player1 = tron.Player(y,x, tron.Orientation.N)
            player2 = tron.Player(y+np.random.randint(1,5),x+np.random.randint(1,5), tron.Orientation.N)
            assert player1.front_crash(player2) is False
            assert player2.front_crash(player1) is False

    def test_front_crash_true(self):
        for ii in range(100):
            x = np.random.randint(0,100)
            y = np.random.randint(0, 100)
            player1 = tron.Player(y,x, tron.Orientation.N)
            player2 = tron.Player(y,x, tron.Orientation.N)
            assert player1.front_crash(player2) is True
            assert player2.front_crash(player1) is True

class TestTron():

    def test_reset_size(self):
        for size in range(10, 20): 
            game = tron.Tron(size=size, num_players=1)
            observation = game.reset()
            # check grid size
            np.testing.assert_equal(observation['board'].shape, (size, size, 2))

            # check walls on border
            self._check_border(observation['board'])
        

    def test_reset_players(self):
        for num_players in range(1,10):
            game = tron.Tron(size=10, num_players=num_players)
            observation = game.reset()
            assert len(observation['positions']) == num_players
            assert observation['board'].shape[2] == num_players+1
            assert len(observation['orientations']) == num_players

    def _check_border(self,board):
        # check for walls on the edge
        np.testing.assert_equal(board[0,:,0], np.ones(board[0,:,0].shape))
        np.testing.assert_equal(board[-1,:,0], np.ones(board[-1,:,0].shape))
        np.testing.assert_equal(board[:,0,0], np.ones(board[:,0,0].shape))
        np.testing.assert_equal(board[:,-1,0], np.ones(board[:,-1,0].shape))

    def test_update(self):
        game = tron.Tron(size=100,num_players=1)
        for ii in range(100):
            game.reset()
            # set player position
            x = np.random.randint(1, 100)
            y = np.random.randint(1, 100)
            game.players[0].x = x
            game.players[0].y = y
            # update game board
            game._update()
            obs = game._get_observation()
            assert obs['board'][y,x,1] == 1
            assert np.sum(obs['board'][:,:,1]) == 2 # there is always a random starting point 

    def test_move(self):
        pass


