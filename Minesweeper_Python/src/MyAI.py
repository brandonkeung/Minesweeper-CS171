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
		self._startY = startY
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
		self._visited = {(startX, startY)}
		neighbors_coord = self.generate_neighbors(self._startX, self._startY)
		for i in neighbors_coord:
			self.action_queue.put(i)

		#print_board(self._board)

	def getAction(self, number: int) -> "Action Object":
		print_board(self._board)
		print("MOVE COUNT:", self._moveCount)

		if self._uncover[0]:
			x, y = self._uncover[1]

			row = self._rowDimension- 1 - self._uncover[1][1] #y value
			self._board[row][self._uncover[1][0]] = number
			self._uncover = (False, (-1, -1))

			if number == 0:
				neighbors = self.generate_neighbors(x, y)
				for i in neighbors:
					if i not in self._visited:
						self.action_queue.put(i)
			# 		if self._board[self._rowDimension - 1 - i[1]][i[0]] == -1:
					

		if (not self.action_queue.empty()):
			print(self._visited)
			# uncover tiles
			x, y = self.action_queue.get()
			self._visited.add((x,y))
			print(f'Currently uncovering {x} and {y}')
			self._uncover = (True, (x, y))
			self._moveCount += 1
			return Action(AI.Action(1), x, y)
	
		
		if self._uncovered_tiles == self._safe_spaces:  # we won the game
			print("win")
			return Action(AI.Action(LEAVE))
		print("Leaving...")
		return Action(AI.Action(LEAVE))
		


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