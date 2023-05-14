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

		self._board = [[-1 for _ in range(colDimension)] for _ in range(rowDimension)]  #board[][]
		self._board[rowDimension - 1 - self._startY][self._startX] = 0  # leave the x the same but +1 and negate for y since we start at bottom left
		
		self._uncovered_tiles = 0
		self._safe_spaces = colDimension*rowDimension - totalMines

		self._uncover = (False, (-1, -1))
		self.action_queue = Queue()
		for i in self.generate_neighbors(self._startX, self._startY):
			self.action_queue.put(i)

		#print_board(self._board)

	def getAction(self, number: int) -> "Action Object":
		print_board(self._board)
		if self._uncover[0]:
			row = self._rowDimension- 1 - self._uncover[1][1] 
			self._board[row][self._uncover[2][0]] = number
			self._uncover = (False, -1, -1)

		if (not self.action_queue.empty()):
			# uncover tiles
			x, y = self.action_queue.get()
			print(x + 1, y + 1)
			self._uncover = (True, (x, y))
			self._moveCount += 1
			return Action(AI.Action(UNCOVER), 2, 2)
	
		#
		# if self._uncovered_tiles == self._safe_spaces:  # we won the game
		# 	print("win")
		# 	return Action(AI.Action(LEAVE))
		# return Action(AI.Action(LEAVE))
		#


	def generate_neighbors(self, x, y) -> list:
		coords = [(x-1,y), (x-1, y-1), (x,y-1), (x+1,y-1), (x + 1,y), (x+1,y+1), (x,y+1), (x-1,y+1)]

		for c in coords[:]:
			if c[0] < 0 or c[0] > self._colDimension - 1:
				coords.remove(c)
			elif c[1] < 0 or c[1] > self._rowDimension - 1:
				coords.remove(c)

		print(coords)
		return coords

	
def print_board(board):
	for i in board:
		print(i)
	print("-----------------")


# run with  python3 Main.py -f .\Problems\Easy_world_1.txt for one world
# run with  python3 Main.py -f .\Problems\ for all worlds

# run with  python Main.py -f .\Problems\Easy_world_1.txt for one world
# run with  python Main.py -f .\Problems\ for all worlds