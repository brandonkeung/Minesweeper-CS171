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
from datetime import datetime

LEAVE = 0
UNCOVER = 1
FLAG = 2
UNFLAG = 3		



class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		##print(startX, startY, rowDimension, colDimension, totalMines)

		self._coveredTile = 0 # 2 kinds marked (know there is mine) or unmakred (dont know)
		self._startX = startX
		self._startY = startY
		self._rowDimension = rowDimension
		self._colDimension = colDimension
		self._totalMines = totalMines
		self._moveCount = 0
		self._uncovered_tiles = 0
		self._safe_spaces = colDimension*rowDimension - totalMines

		self._model =  [[]]
		self._create_model()

		self._board = [[-1 for _ in range(colDimension)] for _ in range(rowDimension)]  #board[][]
		self._board[self._startY][self._startX] = 0
		

		self._uncover = (False, (-1, -1))  # if we uncover, store the coordinates here and set to True

		self.action_queue = Queue()  # queue for keeping trach of uncover events to execute
		neighbors_coord = self.generate_neighbors(self._startX, self._startY)  # generate neighbors of start node
		for i in neighbors_coord:
			self.action_queue.put(i)  # add neighbors to queue since everything around our start node is not a bomb

		# #print("#printing initial model followed by the board")
		# #print_model(self._model)
		# #print_board(self._board)

		#model checking variables
		self._covered_unmarked_frontier = Queue()
		self._uncovered_frontier = Queue()

	def getAction(self, number: int) -> "Action Object":
		##print_board(self._board)
		###print("MOVE COUNT:", self._moveCount)
		###print("SIZE OF QUEUE", self.action_queue.qsize())
		###print("NUM VISITED", len(self._visited))

		if self._uncover[0]:  # if our previous action was uncover, update the board based on 'number'
			x, y = self._uncover[1]

			self._model[y][x].label = number
			self._model[y][x].effective_label = number
			self._update_model(x, y, 0)
			#print("NEW TILE UNLOCKED: ", x, y, number)
			#print(self._moveCount)
			#print_model(self._model)
			self._uncover = (False, (-1, -1))
			
			if number == 0:  # if the number is 0, add the neighbors into the queue since there isn't a bomb around it
				neighbors = self.generate_neighbors(x, y)
				###print("NEIGHBORS", neighbors)
				for i in neighbors:
					###print(i)
					if self._model[i[1]][i[0]].label == "*":
						###print("add")
						self.action_queue.put(i)

		if (not self.action_queue.empty()):   #if our action queue is not empty, uncover
			# while self._board[y][x] != -1:
			# 	if self.action_queue.empty():
			# 		break
			# 	x, y = self.action_queue.get()

			x, y = self.action_queue.get()   # !DESIGN: could be better in do while loop if that exists in python
			found = True
			while self._model[y][x].label != "*":  # find a tile that is unvisited
				if self.action_queue.empty():
					found = False
					break
				x, y = self.action_queue.get()

			###print(f'Currently uncovering {x} and {y}')
			if found:
				self._uncover = (True, (x, y))
				self._moveCount += 1
				self._uncovered_tiles += 1

				# ##print("#printing initial model followed by the board")
				# #print_model(self._model)
				# #print_board(self._board)
				
				return Action(AI.Action(UNCOVER), x, y)
		
		#print("in else")
		# if self._covered_unmarked_frontier.empty():  #!DESIGN: this would be better to generate this frontier or set as we perform actions, should also implement the other thing in slides
		# 	unmarked_neighbors = set()
		# 	for y, row in enumerate(self._model):  
		# 		for x, tile in enumerate(row):
		# 			if type(tile.label) is int and tile.unvisited_neighbors > 0:
		# 				neighbors = self.generate_neighbors(x, y)
		# 				found = 0
		# 				for n in neighbors:
		# 					if n in unmarked_neighbors:
		# 						continue
		# 					if found == tile.unvisited_neighbors:
		# 						break
		# 					if self._model[n[1]][n[0]].label == "*":
		# 						unmarked_neighbors.add(n)
		# 	for u in unmarked_neighbors:
		# 		self._covered_unmarked_frontier.put(u)
			
		if self._uncovered_frontier.empty(): #!DESIGN: could be better as a set for easy removal if make this in place
			for y, row in enumerate(self._model):  
				for x, tile in enumerate(row):
					if type(tile.label) is int and tile.unvisited_neighbors > 0:
						self._uncovered_frontier.put((x,y))				

		while not self._uncovered_frontier.empty():
			##print("IN WHILE")
			cur_X, cur_Y = self._uncovered_frontier.get()
			tile = self._model[cur_Y][cur_X]
			##print(cur_X, cur_Y)
			#print(tile)
			if tile.effective_label == 1 and tile.unvisited_neighbors == 1: # we have 1 bomb left and 1 unvsited/unmarked neighbor
				neighbors = self.generate_neighbors(cur_X,cur_Y)
				for n in neighbors:
					##print(n)
					if self._model[n[1]][n[0]].label == "*":  # found bomb, yay
						#print_model(self._model)
						self._model[n[1]][n[0]].label = "M"
						self._update_model(n[0], n[1], "M")
						#print_model(self._model)
						#change this after minimal ai
						#######################################################
						bomb_neighbors = self.generate_neighbors(n[0], n[1]) 
						for b in bomb_neighbors:
							self.action_queue.put(b)
						#######################################################
						self._moveCount += 1
						return Action(AI.Action(FLAG), n[0], n[1])

			# for y, row in enumerate(self._board):
			# 	found_bomb = True
			# 	if 1 in row:
			# 		for x, num in enumerate(row):
			# 			###print("COORD", x, y)
			# 			if num == 1:
			# 				###print("COORD", x, y)
			# 				neighbors = self.generate_neighbors(x, y)
			# 				potential_bombs = list()
			# 				for n in neighbors:
			# 					if len(potential_bombs) == 2:
			# 						found_bomb = False
			# 						break
			# 					if self._board[n[1]][n[0]] == -1:
			# 						potential_bombs.append(n)
			# 				if found_bomb and len(potential_bombs) == 1:
			# 					x1,y1 = potential_bombs[0]
			# 					self._board[y1][x1] = "F"
			# 					for n in self.generate_neighbors(x1, y1):
			# 						self.action_queue.put(n)
			# 					self._moveCount += 1
			# 					return Action(AI.Action(FLAG), x1, y1)
							
		if self._uncovered_tiles == self._safe_spaces:  # we won the game
			##print("win")
			#print(self._moveCount)
			return Action(AI.Action(LEAVE))
		##print("Leaving...")
		##print_board(self._board)
		#print(self._moveCount)
		return Action(AI.Action(LEAVE))
		


	def generate_neighbors(self, x, y) -> list:
		"""
		Generates the neighbors of a given coordinate.
		Returns a list of valid coordinates given board dimensions.
		"""
		coords = [(x-1,y), (x-1, y-1), (x,y-1), (x+1,y-1), (x + 1,y), (x+1,y+1), (x,y+1), (x-1,y+1)]

		for c in coords[:]:
			if c[0] < 0 or c[0] > self._colDimension - 1:
				coords.remove(c)
			elif c[1] < 0 or c[1] > self._rowDimension - 1:
				coords.remove(c)

		###print(f'Neighbors of {x}, {y} are: {coords}')
		return coords
	
	def _create_model(self):
		"""
		Creates model.
		Model Definition
		-------------------
		first: index label
		second: effective label
		third: # of adjacent covered/unmarked tiles
		* = Covered/Unmarked/Unvisited
		M = mine(Covered/Marked)
		n = label(Uncovered) or number of mines nearby
		----------------------
		"""
		#my_tuple = MyTuple(label='Example', effective_label='Effective', numofneighbors=5)['*', None, 8]
		self._model = [[Tile('*', None, 8) for _ in range(self._colDimension)] for _ in range(self._rowDimension)]
		# set top and bottom borders to ['*', None, 5]
		for col_num in range(len(self._model[0])):
			self._model[0][col_num] = Tile('*', None, 5)
		for col_num in range(len(self._model[-1])):
			self._model[-1][col_num] = Tile('*', None, 5)
		# set left and right borders to ['*', None, 5]
		for row_num in range(len(self._model)):
			for cell_num in range(len(self._model[row_num])):
				if (cell_num == 0 or cell_num == len(self._model[row_num]) - 1):
					self._model[row_num][cell_num] = Tile('*', None, 5)
		# set corners to ['*', None, 3]
		self._model[0][0] = Tile('*', None, 3)
		self._model[0][len(self._model[0]) - 1] =Tile('*', None, 3)
		self._model[len(self._model) - 1][0] = Tile('*', None, 3)
		self._model[len(self._model) - 1][len(self._model[0]) - 1] = Tile('*', None, 3)

		self._model[self._startY][self._startX].label = 0
		self._model[self._startY][self._startX].effective_label = 0

		
		self._update_model(self._startX, self._startY, 0)

	def _update_model(self, x, y, tile_label):  # default is -1 for actions that don't return a 'number'
		neighbors = self.generate_neighbors(x,y)
		for n in neighbors:
			n_X, n_Y = n
			tile_to_update = self._model[n_Y][n_X]

			# update unmarked neighbor count
			if tile_to_update.unvisited_neighbors > 0:  
				tile_to_update.unvisited_neighbors -= 1  

			# update effective label
			if type(tile_label) is str and type(tile_to_update.effective_label) is int:
				tile_to_update.effective_label -= 1
			

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
# python Main.py -f .\ProblemsBeginner\Beginner_world_1.txt

# in openlab
# python Main.pyc -f ./Problems


class Tile():
	def __init__(self, label, effective_label, unvisited_neighbors) -> None:
		self.label = label
		self.effective_label = effective_label
		self.unvisited_neighbors = unvisited_neighbors
	
	def __repr__(self):
		return  "[" + str(self.label) + ", " + str(self.effective_label) + ", " + str(self.unvisited_neighbors) + "]"
