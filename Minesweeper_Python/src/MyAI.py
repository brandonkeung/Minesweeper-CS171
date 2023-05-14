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
		print(startX, startY, rowDimension, colDimension, totalMines)

		self._coveredTile = 0 # 2 kinds marked (know there is mine) or unmakred (dont know)
		self._startX = startX
		self._startY = startY
		self._rowDimension = rowDimension
		self._colDimension = colDimension
		self._totalMines = totalMines
		self._moveCount = 0

		self._model = [[['*', None, 8] for _ in range(colDimension)] for _ in range(rowDimension)]
		# set top and bottom borders to ['*', None, 5]
		for col_num in range(len(self._model[0])):
			self._model[0][col_num] = ['*', None, 5]
		for col_num in range(len(self._model[-1])):
			self._model[-1][col_num] = ['*', None, 5]
		# set left and right borders to ['*', None, 5]
		for row_num in range(len(self._model)):
			for cell_num in range(len(self._model[row_num])):
				if (cell_num == 0 or cell_num == len(self._model[row_num]) - 1):
					self._model[row_num][cell_num] = ['*', None, 5]
		# set corners to ['*', None, 3]
		self._model[0][0] = ['*', None, 3]
		self._model[0][len(self._model[0]) - 1] = ['*', None, 3]
		self._model[len(self._model) - 1][0] = ['*', None, 3]
		self._model[len(self._model) - 1][len(self._model[0]) - 1] = ['*', None, 3]

		self._model[rowDimension - 1 - self._startY][self._startX][0] = '0'
		uncovered_neighbors = self.generate_neighbors(self._startX, self._startY)
		for x, y in uncovered_neighbors:
			row = self._rowDimension- 1 - y
			self._model[row][x][2] = self._model[row][x][2] - 1

		# model definition
		# first index label
		# second effective label
		# third # of adjacent covered/unmarked tiles
		# * = Covered/Unmarked/Unvisited
		# M = mine(Covered/Marked)
		# n = label(Uncovered) or number of mines nearby

		

		
		self._board = [[-1 for _ in range(colDimension)] for _ in range(rowDimension)]  #board[][]
		self._board[self._startY][self._startX] = "0"  
		
		self._uncovered_tiles = 0
		self._safe_spaces = colDimension*rowDimension - totalMines

		self._uncover = (False, (-1, -1))
		self.action_queue = Queue()
		self._visited = {(startX, startY)}
		neighbors_coord = self.generate_neighbors(self._startX, self._startY)
		for i in neighbors_coord:
			self.action_queue.put(i)
		#print("printing initial model followed by the board")
		print_model(self._model)
		print_board(self._board)

	def getAction(self, number: int) -> "Action Object":
		#print_board(self._board)
		#print("MOVE COUNT:", self._moveCount)
		#print("SIZE OF QUEUE", self.action_queue.qsize())
		#print("NUM VISITED", len(self._visited))

		if self._uncover[0]:
			x, y = self._uncover[1]

			self._board[y][x] = number
			self._uncover = (False, (-1, -1))

			if number == 0:
				neighbors = self.generate_neighbors(x, y)
				#print("NEIGHBORS", neighbors)
				for i in neighbors:
					#print(i)
					if self._board[i[1]][i[0]] == -1:
						#print("add")
						self.action_queue.put(i)
			# 		if self._board[self._rowDimension - 1 - i[1]][i[0]] == -1:
					

		if (not self.action_queue.empty()):
			#print(self._visited)
			# uncover tiles
			x, y = self.action_queue.get()
			while self._board[y][x] != -1:
				if self.action_queue.empty():
					break
				x, y = self.action_queue.get()


			self._visited.add((x,y))
			#print(f'Currently uncovering {x} and {y}')
			self._uncover = (True, (x, y))
			self._moveCount += 1
			self._uncovered_tiles += 1
			return Action(AI.Action(UNCOVER), x, y)
		else:
			#print("in else")
			for y, row in enumerate(self._board):
				found_bomb = True
				if 1 in row:
					for x, num in enumerate(row):
						#print("COORD", x, y)
						if num == 1:
							#print("COORD", x, y)
							neighbors = self.generate_neighbors(x, y)
							potential_bombs = list()
							for n in neighbors:
								if len(potential_bombs) == 2:
									found_bomb = False
									break
								if self._board[n[1]][n[0]] == -1:
									potential_bombs.append(n)
							if found_bomb and len(potential_bombs) == 1:
								x1,y1 = potential_bombs[0]
								self._board[y1][x1] = "F"
								for n in self.generate_neighbors(x1, y1):
									self.action_queue.put(n)
								self._moveCount += 1
								return Action(AI.Action(FLAG), x1, y1)
							
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

		#print(f'Neighbors of {x}, {y} are: {coords}')
		return coords

def print_model(model):
	print("-----------------")
	
	for i in model:
		print(i)
	print("-----------------")

	

def print_board(board):
	print("-----------------")
	for i in board:
		print(i)
	print("-----------------")


# run with  python3 Main.py -f .\Problems\Easy_world_1.txt for one world
# run with  python3 Main.py -f .\Problems\ for all worlds

# run with  python Main.py -f .\Problems\Easy_world_1.txt for one world
# run with  python Main.py -f .\Problems\ for all worlds