# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action
import random
from queue import Queue

LEAVE = 0
UNCOVER = 1
FLAG = 2
UNFLAG = 3
		

class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		self._coveredTile = 0 # 2 kinds marked (know there is mine) or unmakred (dont know)
		self._startX = startX
		self._startY = colDimension - 1 - startY
		self._rowDimension = rowDimension
		self._colDimension = colDimension
		self._totalMines = totalMines
		print(startX, startY, rowDimension, colDimension, totalMines)
		self._moveCount = 0

		self._board = [[-1 for _ in range(colDimension)] for _ in range(rowDimension)]
		self._board[self._startY][self._startX] = 0  # leave the x the same but +1 and negate for y since we start at bottom left
		
		self._uncovered_tiles = 0
		self._safe_spaces = colDimension*rowDimension - totalMines

		self.action_queue = Queue()
		print_board(self._board)

	def getAction(self, number: int) -> "Action Object":
		print_board(self._board)
		if (not self.action_queue.empty()):
		# if the current tile is 0 uncover everything around it
			if (self._startX - 1 > -1):
				action = AI.Action(1)
				return Action(action, self._startX - 1, y)
		# if the current tile is 1 


		action = AI.Action(random.randrange(1, len(AI.Action)))
		x = random.randrange(self._colDimension)
		y = random.randrange(self._rowDimension)
		self._moveCount += 1
		return Action(action, x, y)

		action = AI.Action(random.randrange(len(AI.Action)))
		x = random.randrange(self._colDimension)
		y = random.randrange(self._rowDimension)

		print("ACTION", action, " NUMBER", number, "COORDS", x, y)

		if self._uncovered_tiles == self._safe_spaces:  # we won the game
			print("win")
			return Action(AI.Action.LEAVE)
		
		return Action(action, x, y)


def print_board(board):
	for i in board:
		print(i)


# run with  python3 Main.py -f .\Problems\Easy_world_1.txt for one world
# run with  python3 Main.py -f .\Problems\ for all worlds

# run with  python Main.py -f .\Problems\Easy_world_1.txt for one world
# run with  python Main.py -f .\Problems\ for all worlds