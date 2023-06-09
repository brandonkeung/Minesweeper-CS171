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
from collections import defaultdict
import time

LEAVE = 0
UNCOVER = 1
FLAG = 2
UNFLAG = 3		



class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		### print(startX, startY, rowDimension, colDimension, totalMines)

		self.poop = True
		self._coveredTile = 0 # 2 kinds marked (know there is mine) or unmakred (dont know)
		self._startX = startX
		self._startY = startY
		self._rowDimension = rowDimension
		self._colDimension = colDimension
		self._totalMines = totalMines
		self._moveCount = 0
		self._uncovered_tiles = 1
		self._safe_spaces = colDimension*rowDimension - totalMines

		self._mines_found = 0

		self._model =  [[]]
		self._create_model()

		self._board = [[-1 for _ in range(colDimension)] for _ in range(rowDimension)]  #board[][]
		self._board[self._startY][self._startX] = 0
		

		self._uncover = (False, (-1, -1))  # if we uncover, store the coordinates here and set to True

		self.actions_to_execute = set()  # set for keeping trach of uncover events to execute
		neighbors_coord = self.generate_neighbors(self._startX, self._startY)  # generate neighbors of start node
		for i in neighbors_coord:
			self.actions_to_execute.add((i, UNCOVER))  # add neighbors to set since everything around our start node is not a bomb
		# self.actions_to_execute.add(((3, 4), UNCOVER))
		# self.actions_to_execute.add(((2, 5), UNCOVER))
		# ## print("#printing initial model followed by the board")
		#print_model(self._model)
		# #print_board(self._board)

		#model checking variables
		self._covered_unmarked_frontier = set()  # tiles that are covered but are neighbors of our uncovered frontier
		self._uncovered_frontier = set()   # tiles that have been uncovered but not solved..

	def getAction(self, number: int) -> "Action Object":
		#print("action")
		# print("\nBEFORE ACTION")
		# print("Uncovered Frontier", self._uncovered_frontier)
		# print("Covered Marked Frontier", self._covered_unmarked_frontier)
		# print("Known Actions", self.actions_to_execute)
	#	print_model(self._model)


		
		

		if self._uncover[0]:  # if our previous action was uncover, update the board based on 'number'
			x, y = self._uncover[1]
			current_tile = self._model[y][x]
			current_tile.label = number
			current_tile.effective_label = number
			self._update_model(x, y, current_tile.label)

		#	print("NEW TILE UNLOCKED: ", x, y, number)
			#print_model(self._model)
			self._uncover = (False, (-1, -1))
			
			# check how model changed the neighbors
			neighbors = self.generate_neighbors(x, y)
			for i in neighbors:
				if current_tile.effective_label == 0 and self._model[i[1]][i[0]].label == "*" :  # if the number is 0, add the neighbors into the queue since there isn't a bomb around it
				#	print("\tadding uncover at ({}, {})".format(i[0],i[1]))
					self.actions_to_execute.add((i, UNCOVER))
					self.remove_covered_unmarked_neighbors(i)
					continue
				neighbor_tile = self._model[i[1]][i[0]]
				if neighbor_tile.effective_label and neighbor_tile.effective_label == neighbor_tile.unvisited_neighbors:
					## print(self._covered_unmarked_frontier)
					for cu in self._covered_unmarked_frontier.copy():
						if is_neighbor(cu, i) and self._model[cu[1]][cu[0]] == "*":
						#	print("\tadding flag at ({}, {})".format(cu[0], cu[1]))
							self.actions_to_execute.add((cu, FLAG))
							self.remove_covered_unmarked_neighbors(cu)

			if current_tile.effective_label > 0:  # greater than 0 -> add to uncovered_frontier
				self._uncovered_frontier.add((x, y))
				self.append_covered_unmarked_neighbors((x,y))
			# print("Uncovered Frontier", self._uncovered_frontier)
			# print("Covered Marked Frontier", self._covered_unmarked_frontier)
			# print("Known Actions", self.actions_to_execute)
		if len(self._uncovered_frontier) != 0:
			for coord in list(self._uncovered_frontier):
				## print("coord to process", coord)
				x, y = coord
				tile = self._model[y][x]
				if tile.effective_label == 0 and tile.unvisited_neighbors: # uncover all neighbors
					# should use covered_unmarked frontier instead of generating neighbors lol
					###########################################
					neighbors = self.generate_neighbors(x,y)
					for n in neighbors:
						if self._model[n[1]][n[0]].label == "*": 
							self.actions_to_execute.add((n, UNCOVER))
							self.remove_covered_unmarked_neighbors(n)
					###########################################
				elif tile.effective_label == tile.unvisited_neighbors:  # flag all neighbors
					## print("FOUND BOMBS")
					self._uncovered_frontier.remove(coord)
					neighbors = self.generate_neighbors(x, y)
					for n in neighbors:
						### print(n)
						if self._model[n[1]][n[0]].label == "*":  # found bomb(s) so add flag action
							self.actions_to_execute.add(((n[0], n[1]), FLAG))
							self.remove_covered_unmarked_neighbors(n)
				elif len(self.actions_to_execute) == 0:
				#	# print("PATTERN")
					self.check_pattern(coord)
					# check patters
					# check model
		#poop = True
		if len(self.actions_to_execute) == 0 and self._uncovered_tiles != self._safe_spaces:# and self.poop:
			#backtrack
			print(len(self._uncovered_frontier), len(self._covered_unmarked_frontier))
			##REMOVE
		#	if not( len(self._uncovered_frontier) > 25 and len(self._covered_unmarked_frontier) > 40):

			self.poop = False
		#	print("BACKTRACK")
			potential_assignments = self.backtracking_search()
			# print("potential assignments\n", potential_assignments)
			# print("POOOP", len(potential_assignments))
			print("NUM MINES", self._mines_found)
			self.assess_potential_assignments(potential_assignments)
			#print("ACTIONS AFTER BT", len(self.actions_to_execute))
			#x = [{(2, 4): [M, None, 7], (3, 4): [Not Mine, None, 5], (4, 3): [Not Mine, None, 6], (3, 7): [Not Mine, None, 3], (7, 3): [Not Mine, None, 4], (7, 6): [M, None, 1], (2, 5): [Not Mine, None, 7], (7, 4): [Not Mine, None, 2], (7, 7): [Not Mine, None, 1], (3, 3): [M, None, 7], (2, 6): [Not Mine, None, 7], (3, 6): [M, None, 4], (5, 3): [M, None, 5], (6, 3): [Not Mine, None, 6]}]
			
			# TO IMPLEMENT: get best moves based on backtracking search
			# for coord, tile in potential_assignments[0].items():
			# 	if tile.label == "M":
			# 		self.actions_to_execute.add((coord, FLAG))
			# 	else:
			# 		self.actions_to_execute.add((coord, UNCOVER))

		if (len(self.actions_to_execute) != 0):   #if our action queue is not empty, do actions

			coord, action = self.actions_to_execute.pop()
			print("ACTION TO EXECUTE", coord, action)
			x, y = coord
			if action == UNCOVER:
				self._uncover = (True, (x, y))
				self._moveCount += 1
				self._uncovered_tiles += 1
				
				# print("UNCOVER AT: ", x, y)
				self.remove_covered_unmarked_neighbors((x,y))
				return Action(AI.Action(UNCOVER), x, y)
			elif action == FLAG:
				self._moveCount += 1


				# update board for flag
				self._model[y][x].label = "M"
				self._update_model(x, y, "M")

				# print_model(self._model)
				# print("FLAG ACTION: ", x, y)
				self.remove_covered_unmarked_neighbors((x,y))
				self._mines_found += 1
				return Action(AI.Action(FLAG), x, y)
							
		if self._uncovered_tiles == self._safe_spaces:  # we won the game
			print("Completed Board...")			
			return Action(AI.Action(LEAVE))
		
		## print(self._uncovered_tiles, self._safe_spaces)

		print("Leaving...")
		#print_model(self._model)
		# # print("Uncovered Frontier", self._uncovered_frontier)
		# # print("Covered Marked Frontier", self._covered_unmarked_frontier)
		# # print("Known Actions", self.actions_to_execute)

	#	print_model(self._model)
		# potential_assignments = self.backtracking_search()
		# self.assess_potential_assignments(potential_assignments)
		# print(len(self.actions_to_execute))
		##print_board(self._board)
		## print(self._moveCount)
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

		#### print(f'Neighbors of {x}, {y} are: {coords}')
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
		# 1. order variables in V (covered_unmarked_frontier)
		# -----> ordering by num of unvisitied neighbors
		print("IN BACKTRACKING")
		print_model(self._model)
		if len(self._covered_unmarked_frontier) == 0 or len(self._uncovered_frontier) == 0:
			return

		ordered = list()
		for coord in self._covered_unmarked_frontier:
			# get num of neighbors that are in uncovered frontier
			num = len([i for i in self._uncovered_frontier if is_neighbor(i, coord)])
			ordered.append((num, coord))

		ordered_variables = sorted(ordered,key= lambda x:x[0], reverse=True)

		#print("Ordered Variables\n", ordered_variables)
		ordered_ll = create_assignment_LL(ordered_variables)
		constraints = {i: self._model[i[1]][i[0]].copy() for i in self._uncovered_frontier}
		variables = {i: self._model[i[1]][i[0]].copy() for i in self._covered_unmarked_frontier}

		# print("constraints\n", constraints)
		# print("variables\n", variables)
		
		current_var = ordered_ll.head
		constraints_copy = {i: constraints[i].copy() for i in constraints}

		full_complete_assignments = list()
		first_var = ordered_ll.head
		num_of_iterations = 0
		start_time = time.time()
	#	print(len(variables))
		while True:
			#print(ordered_ll.head.value, ordered_ll.head.key)
			#print(current_var.key, current_var.value)
			if current_var.key == (1,0):
				print(variables)
				print(current_var.next)
			if time.time() - start_time > 120:
				print("TIMEOUT")
				break
			
			# print("VAR CURRENTLY ON:", current_var.key, current_var.value)
			if current_var and current_var == first_var and current_var.value and len(current_var.value) == 2:
				print("none")
				break

			
			if current_var and current_var.value == None:
				current_var.value = {"Mine"}
				is_valid, updated_constraints = self._check_update_constraints(current_var.key, "M", constraints_copy)
				# print(constraints_copy)
				if is_valid:
					constraints_copy = updated_constraints
					variables[current_var.key].label = "M"
					# print(current_var.key, "is a Mine")
					# print("\tupdated constraints\n\t", constraints_copy)
					if current_var.next:
						current_var = current_var.next
					
					## print(current_var.key, "is a Mine")
					#continue
				else:
					variables[current_var.key].label = "*"
				continue
			
			if current_var and len(current_var.value) == 1:  # this means we've tried mine on it already so now we try no mine
				if current_var.key == (1,0):
					print("WRONG IF")
				# print(current_var.value, variables[current_var.key].label)
				if variables[current_var.key].label != "*": #this means we're coming from a backtrack since it's been previously assigned
					for c, c_tile in constraints_copy.items():
						if is_neighbor(c, current_var.key):
							c_tile.effective_label += 1
							c_tile.unvisited_neighbors += 1		

				current_var.value.add("Not Mine")
				is_valid, updated_constraints = self._check_update_constraints(current_var.key, "Not Mine", constraints_copy)
				if is_valid:
					variables[current_var.key].label = "Not Mine"
					constraints_copy = updated_constraints
					# print(current_var.key, "is not a mine")
					# print("\tupdated constraints\n\t", constraints_copy)
					if current_var.next:
						current_var = current_var.next
					## print(current_var.key, "is not a mine")
					#continue
				else:
					variables[current_var.key].label = "*"
				continue
			if current_var and current_var.next == None and variables[current_var.key].label != "*": # this means we've reached a complete assignment
				print("FULL ASSIGNMENT")
				# print("\t", variables[(2,4)])
				print(variables)
				full_complete_assignments.append({i: variables[i].copy() for i in variables})
				# print(full_complete_assignments)
				# if len(full_complete_assignments) == 2:
				# 	break
				# TO IMPLEMENT: initiate backtrack to get all potetial assignments
				
			# backtrack
			# print("time to backtrack")
			if not current_var:
				break
			current_var.value = None
			past_label = variables[current_var.key].label
			variables[current_var.key].label = "*"
			if past_label != "*":
				for c, c_tile in constraints_copy.items():
					if is_neighbor(c, current_var.key):
						if past_label == "M":
							c_tile.effective_label += 1
						c_tile.unvisited_neighbors += 1
			
			current_var = current_var.prev
			# print("BACKTRACKED VAL", current_var.key, current_var.value)
			# # print(variables)
			# print("constraints", constraints_copy)
			# # print("stopped")
			if current_var and current_var.prev == None:
				break
		#	break
		
		print(full_complete_assignments)
		return full_complete_assignments
		# for covered in ordered_variables:
		# 	variables[covered].label = "M"
		# 	is_valid, updated_dict = self._check_update_constraints(covered, constraints, variables)
		# 	if is_valid:
		# 		variables = updated_dict
		# 	else:
		# 		variables[covered].label = "No Mine"

	def _check_update_constraints(self, changed_coord, changed_label, constraint_dict:dict) -> tuple:
		"""
		Based on a potential assignment, will check if the constraints are satisfied.
		Returns a tuple that contains (boolean, updated constraint_dict)
		"""
		constraint_dict = {i: constraint_dict[i].copy() for i in constraint_dict}

		for coord in constraint_dict.keys():
		#check constraints
			if is_neighbor(coord, changed_coord):
				t = constraint_dict[coord]
				if t.unvisited_neighbors == 0 or (changed_label == "M" and t.effective_label == 0):# or t.effective_label == 0:
					return (False, dict())
				if changed_label == "Not Mine" and t.effective_label == 1 and t.unvisited_neighbors == 1:
					return (False, dict())
				# passes constrains so update
				if changed_label == "M":
					t.effective_label -= 1
				t.unvisited_neighbors -= 1
	#	# print("\tupdated constraints", constraint_dict)
		return (True, constraint_dict)

	def _update_neighbors(self, changed_coord, constraint_dict):
		"""
		Based on an assignment, this will update neighbors
		"""
		pass


	def check_pattern(self, tile_coord: set):
		"""
		Checks the board for minesweeper patterns and adds actions based on that.
		"""
		x, y = tile_coord
		tile = self._model[y][x]
		
		# get search space?
		uncovered_neighbors = set()
		covered_neighbors = set()

		for coord in self._uncovered_frontier:
			if is_neighbor((x,y), coord):
				uncovered_neighbors.add(coord)
		covered_neighbors = self._get_covered_unmarked_neighbors(tile_coord)
		
		# # print(tile_coord)
		# # print("UN", uncovered_neighbors)
		# # print("CN", covered_neighbors)
		# 1-1-x
		found_actions = False
		if tile.unvisited_neighbors == 2:
			for coordUN in uncovered_neighbors:
				un_x, un_y = coordUN  # un = uncovered neighbor
				if (un_x == x and abs(un_y - y) == 1) or (abs(un_x - x) == 1 and un_y == y): # if neighbor is right next to us
					neighbor_tile = self._model[un_y][un_x]
					if neighbor_tile.effective_label == 1 and neighbor_tile.unvisited_neighbors > 2:
						# print("1-1-x pattern: TRUE")
						covered_neighbors2 = self._get_covered_unmarked_neighbors(coordUN)
						# print("CN2", covered_neighbors2)
						for r in covered_neighbors2.difference(covered_neighbors):
							# print("Adding uncover...")
							####################################
							#shouldn't need if covered_unmarked is correct
							potential_uncover_tile = self._model[r[1]][r[0]]
							if potential_uncover_tile.label == "*":
								self.actions_to_execute.add(((r), UNCOVER))
								found_actions = True
								self.remove_covered_unmarked_neighbors(r)
							# print(r)
						# now get the neighbors of this one from covered unmarked frontier and whichever ones they don't have in common can't be bombs

					 # if neighbor is right next to us and has unvisited > 3
		# 1-2-x
		if not found_actions and tile.effective_label == 1 and tile.unvisited_neighbors in (2, 3):
			for uncovered_coord in uncovered_neighbors:
				un_x, un_y = uncovered_coord
				if (un_x == x and abs(un_y - y) == 1) or (abs(un_x - x) == 1 and un_y == y): # if neighbor is right next to us
					neighbor_tile = self._model[un_y][un_x]
					if neighbor_tile.effective_label == 2 and neighbor_tile.unvisited_neighbors == 3:
						covered_neighbors2 = self._get_covered_unmarked_neighbors(uncovered_coord)
						# print("CN2", covered_neighbors2)
						for r in covered_neighbors2.difference(covered_neighbors):
							# print("Adding uncover...")
							####################################
							#shouldn't need if covered_unmarked is correct
							potential_bomb_tile = self._model[r[1]][r[0]]
							if potential_bomb_tile.label == "*":
								self.actions_to_execute.add(((r), FLAG))
								found_actions = True
								self.remove_covered_unmarked_neighbors(r)
	
	def _get_covered_unmarked_neighbors(self, coord) -> set:
	#	# print("r",self._covered_unmarked_frontier)
		x, y = coord	
		return {c for c in self._covered_unmarked_frontier if is_neighbor((x,y), c)}	


	def append_covered_unmarked_neighbors(self, coord):
		"""
		Appends coord's covered unmarked neighbors
		"""
		c_neighbors = self.generate_neighbors(coord[0], coord[1])
		for n in c_neighbors:
			if (n, 0) in self.actions_to_execute or (n, 1) in self.actions_to_execute:
				# this means the tile is marked
				continue
			n_tile = self._model[n[1]][n[0]]
			if n_tile.label == "*":
				# this means the tile is covered & unmarked
				self._covered_unmarked_frontier.add(n)
	
	def remove_covered_unmarked_neighbors(self, coord):
		"""
		Upon an action, will remove the coord since it would now be considered marked
		"""
		if coord in self._covered_unmarked_frontier:
			self._covered_unmarked_frontier.remove(coord)
	

	def assess_potential_assignments(self, potential_assignments: dict):
		# {coord: {mine: x/y, not mine: x/y })}
		if not potential_assignments or len(potential_assignments) == 0:
			return
		result = defaultdict(int)
		total_assignments = len(potential_assignments)
		keys = potential_assignments[0].keys()
		for assignment in potential_assignments:
			for coord, tile in assignment.items():
				if tile.label == "M":
					result[coord] += 1

		
		# print("RESULT", result)
		actions = set()
		for k in keys:
			if k == (2,6):
				continue
			if result[k] == total_assignments:
				print("adding flag at ", k)
				
				self.actions_to_execute.add((k, FLAG))
				self.remove_covered_unmarked_neighbors(k)
			elif result[k] == 0:
				print("adding uncover at", k)
				self.actions_to_execute.add((k, UNCOVER))
				self.remove_covered_unmarked_neighbors(k)

		# print(self.actions_to_execute)		
		return result


def is_neighbor(a: set, b: set) -> bool:
	"""
	Assuming the coords are valid, returns true if they are neighbors.
	"""
	aX, aY = a
	bX, bY = b
	return False if a == b else abs(aX - bX) in (0, 1) and abs(aY - bY) in (0, 1)

def print_model(model):
	print("-----------------")
	print(" ",end='  ')
	for x in range(len(model)):
		print("{:<13}".format(x), end='')
	print()
	for y, i in enumerate(model):
		print(y, end= '  ')
		for tile in i:
			temp = "{:<13}"
			print(temp.format(str(tile)), end = '')
		print()

	print("-----------------")

	

# def print_board(board):
# 	# print("-----------------")
# 	for i in board:
# 		# print(i)
# 	# print("-----------------")


# run with  python3 Main.py -f .\Problems\Easy_world_1.txt for one world
# run with  python3 Main.py -f .\Problems\ for all worlds

# run with  python Main.py -f .\Problems\Easy_world_1.txt for one world
# run with  python Main.py -f .\Problems\ for all worlds
# run with  python Main.py -f .\ProblemsBeginner\  # 665
# run with  python Main.py -f .\ProblemsIntermediate\ # 552
# run with  python Main.py -f .\ProblemsExpertSmall\ # 8
# python Main.py -f .\ProblemsBeginner\Beginner_world_1.txt
# python Main.py -f .\ProblemsIntermediate\Intermediate_world_1.txt
# python Main.py -f /home/bsteier/Minesweeper-CS171/Minesweeper_Python/src/ProblemsExpertSmall

# in openlab
# python3 Main.pyc -f /home/bsteier/Minesweeper-CS171/Minesweeper_Python/src/ProblemsIntermediate
# run with  python3 Main.pyc -f ./Problems/ #1000
# run with  python3 Main.py -f ./ProblemsBeginner/ # 736
# run with  python3 Main.py -f ./ProblemsIntermediate/ # 673
# python3 Main.pyc -f /home/bsteier/Minesweeper-CS171/Minesweeper_Python/src/ProblemsExpert
# python3 Main.py -f /home/bsteier/Minesweeper-CS171/Minesweeper_Python/src/ProblemsExpertSmall/  16
# python3 Main.py -f /home/bsteier/Minesweeper-CS171/Minesweeper_Python/src/ProblemsExpertSmall/Expert_world_1.txt

# python3 Main.pyc -f /home/bsteier/Minesweeper-CS171/Minesweeper_Python/src/ProblemsExpert/Expert_world_1.txt

class Tile():
	def __init__(self, label, effective_label, unvisited_neighbors) -> None:
		self.label = label
		self.effective_label = effective_label
		self.unvisited_neighbors = unvisited_neighbors
	
	def __repr__(self):
		return  "[" + str(self.label) + ", " + str(self.effective_label) + ", " + str(self.unvisited_neighbors) + "]"

	def copy(self) -> 'Tile':
		return Tile(self.label, self.effective_label, self.unvisited_neighbors)
	
class Node:
	def __init__(self, key:tuple, value=None):
		self.key = key
		self.value = value
		self.next = None
		self.prev = None

class LinkedList:
    def __init__(self):
        self.head = None
	
def printLL(ll):
	temp = ll.head
	while temp:
		# print(temp.key, end=' ')
		temp = temp.next
	# print()
def create_assignment_LL(ordered: list) -> LinkedList:
	result = LinkedList()
	temp = None
	for pair in ordered:
		if temp == None:
			result.head = Node(pair[1])
			temp = result.head
		else:
			temp.next = Node(pair[1])
			temp.next.prev = temp
			temp = temp.next
		
	printLL(result)
	return result

