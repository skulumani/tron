# TRON

AI Tron lightcycle game
Based on hexatron but improved

# Battles

Vary start position
Vary map shape/size
Vary obstacles inside the map
Add point goals inside map (powerups)

## 2 way

1. AI vs. random controller
2. AI vs. human
3. AI vs. AI
4. AI vs. optimal controller
1. AI vs. dumb controller

## n way

1. AI vs. n x AI
2. AI vs. n x random
3. AI vs. n x optimal controller

# TODO 
* [ ] define a state description
    * entire game board at a time
    * vision grid
* [ ] track actions and rewards at each step
    * validate that actions and rewards are being tracked properly
* [ ] record number of visits to each state/action state pair
* [ ] implement monte carlo first visit approach

* [x] no more 45 degree moves
* [.] unit tests for player and game grid - make sure motion works as expected
* [-] test for visualization
* [x] pygame human player interface
* [x] automated testing - save state to some file and playback/print stats
* [x] replay interface - read saved game data
* [ ] pygame recorder
* [x] ensure game end logic works in all situations
    * 1, 2, and n players
    * crash into heads
    * crash into tails
    * crash into walls
    * done flag sometimes not set when everyone dies on same move - check for all dead on same move 
        * done - but it's  draw
* [ ] End game when any player crashes but then restart game with remaining players and same state and continue
* [ ] Automated way to decide on who's the winner after game is done
    * Look at number of states/steps taken by player (maximum is winner?)
    * Look at status flag?
* [ ] Track Elo ratings of each agent and the player


# Player AI

1. [x] Random avoid - pick a random valid move. will never lose unless fully enclosed
7. Semi deterministic - pick only valid moves. Always pick last move unless obstacle - then pick random move. Will only change action when facing an obstacle
2. Ordered
3. Wall hugging
4. Avoid enemy
5. Go to free squares
6. Near vs. Far strategy

# References

* [hexatron](https://github.com/pvmolle/hexatron)
* [pygame_recorder](https://github.com/tdrmk/pygame_recorder)
