
From [here](https://web.archive.org/web/20160507081543/http://csclub.uwaterloo.ca/contest/xiao_strategy.php)

# Robert Xiao's Tron Strategy Guide

Figuring out strategies can be a daunting task. This guide walks you through some simple strategies and provides some tips on building your own killer strategy.

If you haven't already done so, check out the Five Minute Quickstart Guide to submit your first entry.
Sample code is provided in Python, according to this skeleton:

~~~
#!/usr/bin/python

import tron

[code goes here]

# make a move each turn
if __name__ == '__main__':
    for board in tron.Board.generate():
        tron.move(which_move(board))
~~~

Table of Contents

    Random Selection
    Ordered Selection
    Wall-Hugging
    Enemy Avoidance
    Most Open Destination
    Near Strategies
    Far Strategies

## Random Selection

A very simple, naive strategy is to select a direction at random, provided that the destination is clear.

~~~
import random

def which_move(board):
    return random.choice(board.moves())
~~~

Ordered Selection

A refinement of the random selection would be to select directions in a specific order, beginning with a most preferred direction and choosing the next direction if the preferred direction is not available.

ORDER = [tron.NORTH, tron.EAST, tron.SOUTH, tron.WEST]

def which_move(board):
    for dir in ORDER:
        dest = board.rel(dir)

        if board.passable(dest):
            return dir
    return tron.NORTH

Wall-Hugging

Wall hugging is a simple strategy which attempts to move onto a square adjacent to a wall, thus "hugging" the wall by following it around.

It is very space-efficient and will perform well in a survival situation.

import random

# preference order of directions
ORDER = list(tron.DIRECTIONS)
random.shuffle(ORDER)

def which_move(board):

    decision = board.moves()[0]

    for dir in ORDER:

        # where we will end up if we move this way
        dest = board.rel(dir)

        # destination is passable?
        if not board.passable(dest):
            continue

        # positions adjacent to the destination
        adj = board.adjacent(dest)

        # if any wall adjacent to the destination
        if any(board[pos] == tron.WALL for pos in adj):
            decision = dir
            break

    return decision

Enemy Avoidance

Run away! In the game of Tron, if you can't confront the enemy, it's probably best to keep away. In the most simple form, this means not moving to a square which the enemy could also move onto. You can also generalize this to a strategy which simply chooses the destination farthest from the opponent.
Simple form:

ORDER = [tron.NORTH, tron.EAST, tron.SOUTH, tron.WEST]

def which_move(board):
    candidates = []
    for dir in ORDER:
        dest = board.rel(dir)

        if not board.passable(dest):
            continue

        candidates.append(dir)

        adj = board.adjacent(dest)
        if any(board[pos] == tron.THEM for pos in adj):
            continue
        return dir
    if candidates:
        return candidates[0]
    # give up
    return tron.NORTH

More advanced form:

import random

def which_move(board):
    bestdist = 0
    bestmove = tron.NORTH
    for dir in board.moves():
        dest = board.rel(dir)
        dist = (dest[0] - board.them()[0])**2 + (dest[1] - board.them()[1])**2
        if dist > bestdist:
            bestdist = dist
            bestmove = dir
    return bestmove

Most Open Destination

Choice is a good thing in Tron, because it means less chance of being boxed in and trapped. So, a simple but effective strategy is simply to choose the destination square with the most open neighbours. In the case of a tie (which can happen often with a large, empty board), choose any of the above strategies as a fallback.

def which_move(board):
    bestcount = -1
    bestmove = tron.NORTH
    for dir in board.moves():
        dest = board.rel(dir)
        count = 0
        for pos in board.adjacent(dest):
            if board[pos] == tron.FLOOR:
                count += 1
        if count > bestcount:
            bestcount = count
            bestmove = dir
    return bestmove

Near Strategies

When your bot is close to the opponent (say, less than 5 squares away), your objective should be to attack the opponent and try to force him into a corner or reduce his room to move.

Popular strategies at this range primarily consist of variations on the minimax algorithm, in which your bot considers all possible moves which could occur, and uses some scoring system to determine which moves are most advantageous to you and most disadvantageous to your opponent.

Because your bot only has one second to make each move, various techniques must be used to reduce the number of moves to consider; such techniques include alpha-beta pruning and iterative deepening. brikbrik has written up a nice guide on these strategies at http://www.sifflez.org/misc/tronbot/.

This method is best applied when near your opponent because longer distances will increase the depth (number of forward moves) of the search. If your bot is very far away from the opponent, other strategies may be needed.
Far Strategies

When your bot is far away or even isolated from the opponent, strategies change considerably. In the latter case, if you cannot reach the opponent at all, then your goal must be to survive the longest, because the opponent is similarly isolated. In the former case, you can opt for either a survival strategy (which might even involve intentional isolation, if you can mark out more free space than the opponent), or you can opt to move towards him and confront him using your near strategy.

In either case, it is important to consider a good far strategy, since many games begin with an enormous open field with you and your opponent at opposing corners. Game-tree based near strategies perform poorly when far from your opponent, so a good alternate strategy will ensure that you do well from the beginning.
Flood-fill

The flood-fill algorithm determines the size of a connected region on the playing field. You can use this algorithm to move towards the region with largest free space, which generally results in longer survival. However, there are situations where flood-fill can be tricked into entering a trap: an area that looks big, but in which your bot cannot move freely (an example is a "comb" pattern with several corridors only one square wide). So, while this strategy works for most situations and is an easy addition to a good near strategy, it doesn't cover all situations.
Longest-path approximation

What your bot is effectively trying to do in a survival situation is to find the longest path in the board starting at your current position.

Unfortunately, the longest-path problem itself is NP-complete, which means that, barring a miracle in Computer Science (namely, the unlikely result that P=NP), it is very difficult in general to find this longest path.

All hope is not lost, however: there are some decent approximations you can make which run reasonably quickly and avoid traps like those described above.

One such approach is based on articulation vertices on the board. An articulation vertex on a Tron board is a space which, if it were filled in by a wall or trail, would cut the area it is in into two or more disconnected areas. For a given square, if it is an articulation vertex which cuts the area into three or more disconnected areas, then it is impossible for your bot to visit all three areas, which gives you an easy way to determine how many squares are impossible to visit. By computing the articulation vertices in the board, you can obtain a better approximation of the number of free squares which can be visited, and thus fill your space more efficiently.

