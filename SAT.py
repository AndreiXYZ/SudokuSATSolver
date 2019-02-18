from collections import Counter
from itertools import chain
import time
import random
import copy
import math

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


def removeUnitClauses(clauses, truthValues,counter):
	removed = 0
	unitClauses = []
	#build unit clause list and remove units
	try:
		for i in range(len(clauses)):
			if len(clauses[i])==1:
				#check for L and not L being both unit cases
				#TODO
				unitClauses.append(clauses[i][0])

				if clauses[i][0] > 0:
					truthValues[abs(clauses[i][0])] = 1
				else:
					truthValues[abs(clauses[i][0])] = 0
				removeFromCounter(clauses[i],counter)
				del clauses[i]
				removed = 1
	except Exception as e:
		print(e)

	#check if impossible
	for unitClause1 in unitClauses:
		for unitClause2 in unitClauses:
			if unitClause1 == -unitClause2:
				return 'UNSAT'


	for unitClause in unitClauses:
		for idx1, clause in enumerate(clauses):
			for idx2, elem in enumerate(clause):
				#if an element of clause is known to be false, remove it
				if elem == -unitClause:
					removeFromCounter(elem,counter)
					del clauses[idx1][idx2]
					removed = 1
				#if an element of clause is known to be true, remove clause
				if elem == unitClause:
					removeFromCounter(clause,counter)
					del clauses[idx1]
					removed = 1
					break

	return clauses, truthValues, removed


def removePurity(clauses, truthValues,elemCounter):
	removed = 0
	for idx,clause in enumerate(clauses):
		for elem in clause:
			#check if elem is pure
			if elemCounter[elem] > 0 and elemCounter[-elem] == 0:
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


#@timeit
def solveDp(clauses, truthValues,elemCounter):
	'''
	Given a set of rules, (sudoku rules + puzzle)
	find a solution and return it. 
	Uses DP algorithm
	'''

	#Simplify clauses as much as possible
	removed = 1
	while removed:
		removed = 0
		print('Original clauses with size >2: ',len([x for x in clauses if len(x)>2]))
		clauses, removed = removeTautology(clauses,elemCounter)
		print('After tautology clauses with size >2: ',len([x for x in clauses if len(x)>2]))
		clauses, truthValues, removed = removePurity(clauses, truthValues,elemCounter)
		print('After purity clauses with size >2: ',len([x for x in clauses if len(x)>2]))
		clauses, truthValues, removed = removeUnitClauses(clauses, truthValues,elemCounter)

	#Check termination conditions
	if [] in clauses:
		print('UNSAT')
		return clauses,truthValues,'UNSAT'
	if not clauses:
		print('SAT')
		print(truthValues)
		return clauses,truthValues,"SAT"

	print(len(clauses))
	if len(truthValues)==729:
		print(truthValues)
		print(games[0])
	#Backtrack boys
	for literal in randomOrder:
		#if literal already has truth assigned, skip it
		if truthValues.get(literal) is not None:
			continue
		for val in [1,0]:
			tempTruthVals = copy.deepcopy(truthValues)
			tempClauses = copy.deepcopy(clauses)
			tempCounter = copy.deepcopy(elemCounter)
			
			tempTruthVals[literal] = val
			# if val==1:
				# tempClauses.append([literal,0])
				# tempCounter[literal]=tempCounter[literal]+1
			# else:
				# tempClauses.append([-literal,0])
				# tempCounter[-literal]=tempCounter[-literal]+1
			#print(val,literal)
			tempClauses, tempTruthVals, sat = solveDp(tempClauses, tempTruthVals,tempCounter)
			if sat=='SAT':
				return 0,0,'SAT'




if __name__ == "__main__":
	
	sudokuRules = getRules()
	games = readGames(r'test sudokus/1000 sudokus.txt')
	game1 = sudokuRules + games[0]
	print(len(game1))
	c = Counter(list(chain(*game1)))
	randomOrder = [k for k in c.keys() if k>0]
	random.shuffle(randomOrder)
	print(randomOrder)
	newClauses, truthVals, sat = solveDp(game1,{},c)
	print(sat)