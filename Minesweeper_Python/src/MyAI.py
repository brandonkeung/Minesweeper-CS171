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

		self.actions_to_execute = set()  # set for keeping trach of uncover events to execute
		neighbors_coord = self.generate_neighbors(self._startX, self._startY)  # generate neighbors of start node
		for i in neighbors_coord:
			self.actions_to_execute.add((i, UNCOVER))  # add neighbors to set since everything around our start node is not a bomb

		# #print("#printing initial model followed by the board")
		#print_model(self._model)
		# #print_board(self._board)

		#model checking variables
		self._covered_unmarked_frontier = set()  # tiles that are covered but are neighbors of our uncovered frontier
		self._uncovered_frontier = set()   # tiles that have been uncovered but not solved..

	def getAction(self, number: int) -> "Action Object":
		print("\nBEFORE ACTION")
		print(self._uncovered_frontier)
		print(self.actions_to_execute)
		print_model(self._model)
		# print("MOVE COUNT:", self._moveCount)
		# print("SIZE OF QUEUE", self.action_queue.qsize())
		# print("NUM VISITED", len(self._visited))
		
		if self._uncover[0]:  # if our previous action was uncover, update the board based on 'number'
			x, y = self._uncover[1]
			current_tile = self._model[y][x]
			current_tile.label = number
			current_tile.effective_label = number
			self._update_model(x, y, current_tile.label)

			print("NEW TILE UNLOCKED: ", x, y, number)
			print_model(self._model)
			self._uncover = (False, (-1, -1))
			
			if current_tile.effective_label == 0:  # if the number is 0, add the neighbors into the queue since there isn't a bomb around it
				neighbors = self.generate_neighbors(x, y)
				###print("NEIGHBORS", neighbors)
				for i in neighbors:
					###print(i)
					if self._model[i[1]][i[0]].label == "*":
						###print("add")
						self.actions_to_execute.add((i, UNCOVER))
			elif current_tile.effective_label > 0:  # greater than 0 -> add to uncovered_frontier
				self._uncovered_frontier.add((x, y))
			
		if len(self._uncovered_frontier) != 0:
			for coord in list(self._uncovered_frontier):
				#print("coord to process", coord)
				x, y = coord
				tile = self._model[y][x]
				if tile.effective_label == 0 and tile.unvisited_neighbors:
					# should use covered_unmarked frontier instead of generating neighbors lol
					###########################################
					neighbors = self.generate_neighbors(x,y)
					for n in neighbors:
						if self._model[n[1]][n[0]].label == "*": 
							self.actions_to_execute.add(((n[0], n[1]), UNCOVER))
					###########################################
				elif tile.effective_label == tile.unvisited_neighbors:
					#print("FOUND BOMBS")
					self._uncovered_frontier.remove(coord)
					neighbors = self.generate_neighbors(x, y)
					for n in neighbors:
						##print(n)
						if self._model[n[1]][n[0]].label == "*":  # found bomb(s) so add flag action
							self.actions_to_execute.add(((n[0], n[1]), FLAG))

		if (len(self.actions_to_execute) != 0):   #if our action queue is not empty, uncover

			coord, action = self.actions_to_execute.pop()
			x, y = coord
			if action == UNCOVER:
				self._uncover = (True, (x, y))
				self._moveCount += 1
				self._uncovered_tiles += 1
				
				# print("UNCOVER AT: ", x, y)
				return Action(AI.Action(UNCOVER), x, y)
			elif action == FLAG:
				self._moveCount += 1
				self._uncovered_tiles += 1

				# update board for flag
				self._model[y][x].label = "M"
				self._update_model(x, y, "M")

				# print_model(self._model)
				# print("FLAG ACTION: ", x, y)
				return Action(AI.Action(FLAG), x, y)

		
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
			
		# if len(self._uncovered_frontier) == 0: #!DESIGN: could be better as a set for easy removal if make this in place
		# 	for y, row in enumerate(self._model):  
		# 		for x, tile in enumerate(row):
		# 			if type(tile.label) is int and tile.unvisited_neighbors > 0:
		# 				self._uncovered_frontier.add((x,y))				

		# while len(self._uncovered_frontier) != 0:
		# 	##print("IN WHILE")
		# 	cur_X, cur_Y = self._uncovered_frontier.pop()
		# 	print("POP", cur_X, cur_Y)
		# 	tile = self._model[cur_Y][cur_X]

		# 	if tile.effective_label == tile.unvisited_neighbors:
		# 		neighbors = self.generate_neighbors(cur_X,cur_Y)
		# 		for n in neighbors:
		# 			##print(n)
		# 			if self._model[n[1]][n[0]].label == "*":  # found bomb(s) so add flag action
		# 				self.actions_to_execute.add(((n[0], n[1]), FLAG))

		# 				self._moveCount += 1
		# 		break # break out of while loop and execute these actions





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
			print("Completed Board...")			
			return Action(AI.Action(LEAVE))
		print("Leaving...")
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
		current_tile = self._model[y][x]
		for n in neighbors:
			n_X, n_Y = n
			neighbor_tile = self._model[n_Y][n_X]

			# update unmarked neighbor count
			if neighbor_tile.unvisited_neighbors > 0:  
				neighbor_tile.unvisited_neighbors -= 1  

			# update effective label
			# if our tile_label is a string then it's a bomb so we subtract from our effective label
			if type(tile_label) is str and type(neighbor_tile.effective_label) is int:
				neighbor_tile.effective_label -= 1
				if neighbor_tile.effective_label == 0 and neighbor_tile.unvisited_neighbors == 0 and (n_X, n_Y) in self._uncovered_frontier: # this tile is now solved so take out of uncovered frontier
					self._uncovered_frontier.remove((n_X, n_Y))
			
			# updates to our current tile
			# 1. if one of our neighbors is a bomb, then update our effective label
			if neighbor_tile.label == "M" and current_tile.effective_label:
				current_tile.effective_label -= 1
				if current_tile.effective_label == 0 and neighbor_tile.unvisited_neighbors == 0 and (x,y) in self._uncovered_frontier: # this tile is now solved so take out of uncovered frontier
					self._uncovered_frontier.remove((x,y))
	
	def backtracking_search(self):
		pass


	# def check_pattern(self, tile_coord: set) -> list:
	# 	"""
	# 	Checks the board for minesweeper patterns and returns actions based on that.
	# 	"""
	# 	return list()

def print_model(model):
	print("-----------------")
	for i in model:
		for tile in i:
			temp = "{:<13}"
			print(temp.format(str(tile)), end = '')
		print()

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
