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

    def test_act(self):
        pass
