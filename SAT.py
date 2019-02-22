from collections import Counter
from itertools import chain
import time
import random
import copy
import math
import matplotlib.pyplot as plt
import numpy as np
import pickle

def timeit(f):
	#decorator used to time functions
	#works with recursive behavior
	is_evaluating = False
	def g(*args):
		nonlocal is_evaluating
		if is_evaluating:
			return f(*args)
		else:
			start_time = time.process_time()
			is_evaluating = True
			try:
				value = f(*args)
			finally:
				is_evaluating = False
			end_time = time.process_time()
			print(f'time taken for {f.__name__}: {end_time-start_time}')
			return value
	return g


def getRules():
	'''
	Get the general rules of sudoku.
	Format is [[rule1], [rule2], [rule3], ...]
	where each rule is a cnf clause (example: [-112,-113])
	'''
	rules = []
	with open(r'test sudokus/sudoku-rules.txt', 'r') as f:
		#one rule per line
		for line in f:
			rule = line.split()
			if rule[0] == 'p':
				numVars = rule[2]
				numClauses = rule[3]
			elif rule[0] not in ('p', 'c'):
				#map to ints
				rule = list(map(int, rule[:-1]))
				#add rule to our list of rules
				rules.append(rule)
	return rules


def readGames(file):
	'''
	Read all games of sudoku from a file.
	Each line is a string, representing a game.
	A game is basically a set of cnf clauses
	so use the same format as for the Sudoku
	rules (see above).
	'''
	games = []
	with open(file, 'r') as f:
		for game in f:
			gameRules = gameToCnf(game)
			games.append(gameRules)
	return games


def gameToCnf(gameString):
	#Converts game string to CNF rules.
	#Squares that are filled in are an extra constraint
	gameRules = []
	for idx, elem in enumerate(gameString):
		if elem not in ['.', '\n']:
			row = idx//9+1
			col = idx%9+1
			val = row*100+col*10+int(elem)
			gameRules.append([val])
	return gameRules

def removeFromCounter(args,elemCounter):
	if type(args) == list:
		for elem in args:
			if elemCounter[elem] > 0:
				elemCounter[elem] -= 1
	elif type(args) == int:
		if elemCounter[args] > 0:
			elemCounter[args] -= 1


def removeTautology(clauses,counter):
	removed = 0
	try:
		for i in range(len(clauses)):
			if (len(clauses[i]) == 2) and (clauses[i][0]==-clauses[i][1]):
				removeFromCounter(clauses[i],counter)
				del clauses[i]
				removed = 1
	except:
		return clauses, removed
	return clauses, removed


def removeUnitClauses(clauses, truthValues,counter,unitClauses):
	removed = 0
	#build unit clause list and remove units
	try:
		for i in range(len(clauses)):
			if len(clauses[i])==1:
				unitClauses.append(clauses[i][0])
				if -clauses[i][0] in unitClauses:
					#print('UNSAT')
					return 0,0,0,'UNSAT'
				if clauses[i][0] > 0:
					truthValues[abs(clauses[i][0])] = 1
				else:
					truthValues[abs(clauses[i][0])] = 0
				removeFromCounter(clauses[i],counter)
				del clauses[i]
				removed = 1
	except Exception as e:
		pass
		#print(e)




	for idx1, clause in enumerate(clauses):
		for idx2, elem in enumerate(clause):
			#if an element of clause is known to be false, remove it
			if -elem in  unitClauses:# or (elem in truthValues and truthValues[elem]==0):
				removeFromCounter(elem,counter)
				del clauses[idx1][idx2]
				removed = 1
			#if an element of clause is known to be true, remove clause
			if elem in unitClauses:# or (elem in truthValues and truthValues[elem]==1):
				removeFromCounter(clause,counter)
				del clauses[idx1]
				removed = 1
				break

	return clauses, truthValues, removed, unitClauses


def removePurity(clauses, truthValues,elemCounter):
	removed = 0
	for idx,clause in enumerate(clauses):
		for elem in clause:
			#check if elem is pure
			if elemCounter[elem] > 0 and elemCounter[-elem] == 0 and not abs(-elem) in truthValues:
				#print(clause)
				removed = 1
				#assign its truth value
				if elem>0:
					truthValues[abs(elem)] = 1
				else:
					truthValues[abs(elem)] = 0
				#remove clause
				del clauses[idx]
				break
	return clauses, truthValues, removed

def print_sudoku(true_vars):
	"""
	Print sudoku.
	:param true_vars: List of variables that your system assigned as true. Each var should be in the form of integers.
	:return:
	"""
	if len(true_vars) != 81:
		print("Wrong number of variables.")
		return
	s = []
	row = []
	for i in range(len(true_vars)):
		row.append(str(int(true_vars[i]) % 10))
		if (i+1) % 9 == 0:
			s.append(row)
			row = []

	print("╔═" + "═" + "═╦═" + "═" + "═╦═" + "═" + "═╦═" + "═" + "═╦═" + "═" + "═╦═" + "═" + "═╦═" + "═" + "═╦═" + "═" + "═╦═" + "═" + "═╗")
	print("║ "+s[0][0]+" | "+s[0][1]+" | "+s[0][2]+" ║ "+s[0][3]+" | "+s[0][4]+" | "+s[0][5]+" ║ "+s[0][6]+" | "+s[0][7]+" | "+s[0][8]+" ║")
	print("╠─" + "─" + "─┼─" + "─" + "─┼─" + "─" + "─╬─" + "─" + "─┼─" + "─" + "─┼─" + "─" + "─╬─" + "─" + "─┼─" + "─" + "─┼─" + "─" + "─╣")
	print("║ "+s[1][0]+" | "+s[1][1]+" | "+s[1][2]+" ║ "+s[1][3]+" | "+s[1][4]+" | "+s[1][5]+" ║ "+s[1][6]+" | "+s[1][7]+" | "+s[1][8]+" ║")
	print("╠─" + "─" + "─┼─" + "─" + "─┼─" + "─" + "─╬─" + "─" + "─┼─" + "─" + "─┼─" + "─" + "─╬─" + "─" + "─┼─" + "─" + "─┼─" + "─" + "─╣")
	print("║ "+s[2][0]+" | "+s[2][1]+" | "+s[2][2]+" ║ "+s[2][3]+" | "+s[2][4]+" | "+s[2][5]+" ║ "+s[2][6]+" | "+s[2][7]+" | "+s[2][8]+" ║")
	print("╠═" + "═" + "═╬═" + "═" + "═╬═" + "═" + "═╬═" + "═" + "═╬═" + "═" + "═╬═" + "═" + "═╬═" + "═" + "═╬═" + "═" + "═╬═" + "═" + "═╣")
	print("║ "+s[3][0]+" | "+s[3][1]+" | "+s[3][2]+" ║ "+s[3][3]+" | "+s[3][4]+" | "+s[3][5]+" ║ "+s[3][6]+" | "+s[3][7]+" | "+s[3][8]+" ║")
	print("╠─" + "─" + "─┼─" + "─" + "─┼─" + "─" + "─╬─" + "─" + "─┼─" + "─" + "─┼─" + "─" + "─╬─" + "─" + "─┼─" + "─" + "─┼─" + "─" + "─╣")
	print("║ "+s[4][0]+" | "+s[4][1]+" | "+s[4][2]+" ║ "+s[4][3]+" | "+s[4][4]+" | "+s[4][5]+" ║ "+s[4][6]+" | "+s[4][7]+" | "+s[4][8]+" ║")
	print("╠─" + "─" + "─┼─" + "─" + "─┼─" + "─" + "─╬─" + "─" + "─┼─" + "─" + "─┼─" + "─" + "─╬─" + "─" + "─┼─" + "─" + "─┼─" + "─" + "─╣")
	print("║ "+s[5][0]+" | "+s[5][1]+" | "+s[5][2]+" ║ "+s[5][3]+" | "+s[5][4]+" | "+s[5][5]+" ║ "+s[5][6]+" | "+s[5][7]+" | "+s[5][8]+" ║")
	print("╠═" + "═" + "═╬═" + "═" + "═╬═" + "═" + "═╬═" + "═" + "═╬═" + "═" + "═╬═" + "═" + "═╬═" + "═" + "═╬═" + "═" + "═╬═" + "═" + "═╣")
	print("║ "+s[6][0]+" | "+s[6][1]+" | "+s[6][2]+" ║ "+s[6][3]+" | "+s[6][4]+" | "+s[6][5]+" ║ "+s[6][6]+" | "+s[6][7]+" | "+s[6][8]+" ║")
	print("╠─" + "─" + "─┼─" + "─" + "─┼─" + "─" + "─╬─" + "─" + "─┼─" + "─" + "─┼─" + "─" + "─╬─" + "─" + "─┼─" + "─" + "─┼─" + "─" + "─╣")
	print("║ "+s[7][0]+" | "+s[7][1]+" | "+s[7][2]+" ║ "+s[7][3]+" | "+s[7][4]+" | "+s[7][5]+" ║ "+s[7][6]+" | "+s[7][7]+" | "+s[7][8]+" ║")
	print("╠─" + "─" + "─┼─" + "─" + "─┼─" + "─" + "─╬─" + "─" + "─┼─" + "─" + "─┼─" + "─" + "─╬─" + "─" + "─┼─" + "─" + "─┼─" + "─" + "─╣")
	print("║ "+s[8][0]+" | "+s[8][1]+" | "+s[8][2]+" ║ "+s[8][3]+" | "+s[8][4]+" | "+s[8][5]+" ║ "+s[8][6]+" | "+s[8][7]+" | "+s[8][8]+" ║")
	print("╚═" + "═" + "═╩═" + "═" + "═╩═" + "═" + "═╩═" + "═" + "═╩═" + "═" + "═╩═" + "═" + "═╩═" + "═" + "═╩═" + "═" + "═╩═" + "═" + "═╝")

def check_sudoku(true_vars):
	"""
	Check sudoku.
	:param true_vars: List of variables that your system assigned as true. Each var should be in the form of integers.
	:return:
	"""
	import math as m
	s = []
	row = []
	for i in range(len(true_vars)):
		row.append(str(int(true_vars[i]) % 10))
		if (i + 1) % 9 == 0:
			s.append(row)
			row = []

	correct = True
	for i in range(len(s)):
		for j in range(len(s[0])):
			for x in range(len(s)):
				if i != x and s[i][j] == s[x][j]:
					correct = False
					print("Repeated value in column:", j)
			for y in range(len(s[0])):
				if j != y and s[i][j] == s[i][y]:
					correct = False
					print("Repeated value in row:", i)
			top_left_x = int(i-i%m.sqrt(len(s)))
			top_left_y = int(j-j%m.sqrt(len(s)))
			for x in range(top_left_x, top_left_x + int(m.sqrt(len(s)))):
				for y in range(top_left_y, top_left_y + int(m.sqrt(len(s)))):
					if i != x and j != y and s[i][j] == s[x][y]:
						correct = False
						print("Repeated value in cell:", (top_left_x, top_left_y))
	return correct


def get_cp(literal, elemCounter):
	return elemCounter[literal]


def get_cn(literal, elemCounter):
	return elemCounter[-literal]


def dlcs(elemCounter):
	posVals = [elem for elem in elemCounter.keys() if elem>0]
	orderedLiteralList = sorted(posVals, key=lambda x: get_cp(x, elemCounter) + get_cn(x, elemCounter), 
						reverse=True)
	valsList = list(map(lambda x: [0,1] if get_cp(x, elemCounter) < get_cn(x, elemCounter) 
						else [1,0], orderedLiteralList))
	return orderedLiteralList, valsList


def dlis(elemCounter):
	#order them by cp (not actually how it was in the slides)
	posVals = [elem for elem in elemCounter.keys() if elem>0]
	orderedLiteralList = sorted(posVals, key=lambda x: get_cp(x, elemCounter),
								reverse=True)
	valsList = list(map(lambda x: [0,1] if get_cp(x, elemCounter) < get_cn(x, elemCounter) 
						else [1,0], orderedLiteralList))
	return orderedLiteralList, valsList
					
def diagonalsFirst(elemCounter):
	posVals = [elem for elem in elemCounter.keys() if elem>0]
	orderedLiteralList = sorted(posVals, key=lambda x: x%110<10,
								reverse=True)
	valsList=[[1,0] for i in range(0,len(orderedLiteralList))]
	return orderedLiteralList,valsList


@timeit
def solveDp(clauses, truthValues,elemCounter, unitClauses, heuristic=None):
	'''
	Given a set of rules, (sudoku rules + puzzle)
	find a solution and return it. 
	Uses DP algorithm
	'''
	#print(truthValues)
	#Simplify clauses as much as possible
	global backtrackCounter
	removed = 1
	while removed:
		removed = 0
		clauses, removed = removeTautology(clauses,elemCounter)
		clauses, truthValues, removed, unitClauses = removeUnitClauses(clauses, truthValues,elemCounter,unitClauses)
		if unitClauses=="UNSAT":
			backtrackCounter+=1
			return 0,0,"UNSAT"
	clauses, truthValues, removed = removePurity(clauses, truthValues,elemCounter)
	#Check termination conditions
	if [] in clauses:
		#print('UNSAT []')
		backtrackCounter+=1
		return clauses,truthValues,'UNSAT'
	if not clauses:
		#print('SAT')
		answer=sorted([k for k,v in truthValues.items() if v==1])
		#print('ans=',answer)
		#print(games[0])
		#print(len(answer))
		print_sudoku(answer)
		print(check_sudoku(answer))
		return clauses,truthValues,"SAT"

	#print(len(clauses))
	#print(len(truthValues))

	if heuristic is not None:
		order, valsList = heuristic(elemCounter)
	else:
		order = randomOrder

	for idx,literal in enumerate(order):
		#if literal already has truth assigned, skip it
		if truthValues.get(literal) is not None:
			continue

		if heuristic is None:
			valOrder = [1,0]
		else:
			valOrder = valsList[idx]
		
		for val in valOrder:
			tempTruthVals = copy.deepcopy(truthValues)
			tempClauses = copy.deepcopy(clauses)
			tempCounter = copy.deepcopy(elemCounter)
			tempUnitClauses=copy.deepcopy(unitClauses)
			tempTruthVals[literal] = val
			if val==1:
				tempClauses.append([literal])
				tempCounter[literal]=tempCounter[literal]+1
				tempUnitClauses.append(literal)
				#print('literal picked: ',literal)
			else:
				tempClauses.append([-literal])
				tempCounter[-literal]=tempCounter[-literal]+1
				tempUnitClauses.append(-literal)
				#print('literal picked: ',-literal)
			#print(val,literal)
			tempClauses, tempTruthVals, sat = solveDp(tempClauses, tempTruthVals,tempCounter,tempUnitClauses, heuristic)
			if sat=='SAT':
				return 0,0,'SAT'
			elif sat=="UNSAT" and val==valOrder[1]:
				backtrackCounter+=1
				return tempClauses,tempTruthVals,"UNSAT"


if __name__ == "__main__":
	random.seed(42)
	sudokuRules = getRules()


	#build a balanced dataset (num. of clauses per game range 22-31, 147 games each)
	games = readGames(r'test sudokus/subig20.sdk.txt')

	balancedGames = []
	clausesPerGameCounter = Counter()
	for game in games:
		if not(clausesPerGameCounter[len(game)] > 146) and 21 <= len(game) <= 31:
			clausesPerGameCounter[len(game)] += 1
			balancedGames.append(game)

	print(clausesPerGameCounter)
	runtimes = []
	print('dataset size=', len(balancedGames))
	backtrackCounter=0
	backtracks=[]
	for i in range(0,len(balancedGames)):
		game1 = copy.deepcopy(sudokuRules) + copy.deepcopy(balancedGames[i])
		c = Counter(list(chain(*game1)))
		randomOrder = [k for k in c.keys() if k>0]
		#########diag first, comment out if not using############
		#posVals = [elem for elem in c.keys() if elem>0]
		#randomOrder = sorted(posVals, key=lambda x: x%110<10,
		#						reverse=True)
		#randomOrder = sorted(posVals, key=lambda x: (x//100)+(x//10)%10==10,reverse=True)
		#print(randomOrder)
		#########################################################
		t1 = time.process_time()
		solveDp(game1,{},c,[],dlis)
		t2 = time.process_time()
		runtimes.append((len(balancedGames[i]), t2-t1))
		backtracks.append((len(balancedGames[i]),backtrackCounter))
		#print(len(balancedGames[i]))
		print('i: ',i)
		print('btc: ',backtrackCounter)
		backtrackCounter=0
	
	xvals, yvals = zip(*runtimes)
	plt.plot(xvals, yvals, 'ro')
	plt.show()
	
	xvals2, yvals2 = zip(*backtracks)
	plt.plot(xvals2, yvals2, 'ro')
	plt.show()
	
	with open('runtimes_dlis.pkl', 'wb') as f:
		pickle.dump(runtimes, f)
	with open('backtrack_dlis.pkl', 'wb') as f:
		pickle.dump(backtracks, f)