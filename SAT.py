import copy
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

def removeFromCounter(args):
	if type(args) == list:
		for elem in args:
			if elemCounter[elem] > 0:
				elemCounter[elem] -= 1
	elif type(args) == int:
		if elemCounter[elem] > 0:
			elemCounter[elem] -= 1


def removeTautology(clauses):
	removed = 0
	try:
		for i in range(len(clauses)):
			if len(clauses[i]) == 2 and clauses[i][0]==-clauses[i][1]:
				elemCounter = removeFromCounter(clauses[i])
				del clauses[i]
				removed = 1
	except:
		return clauses, removed
	return clauses, removed


def removeUnitClauses(clauses, truthValues):
	removed = 0
	unitClauses = []
	try:
		#build unit clause list 
		for i in range(len(clauses)):
			if len(clauses[i])==1:
				#check for L and not L being both unit cases
				#TODO

				unitClauses.append(clauses[i][0])

				if clauses[i][0] > 0:
					truthValues[abs(clauses[i][0])] = 1
				else:
					truthValues[abs(clauses[i][0])] = 0
				removeFromCounter(clauses[i])
				del clauses[i]
				removed = 1

		#check if impossible
		for unitClause1 in unitClauses:
			for unitClause2 in unitClause:
				if unitClause1 == -unitClause2:
					return 'UNSAT'


		for unitClause in unitClauses:
			for idx1, clause in enumerate(clauses):
				for idx2, elem in enumerate(clause):
					#if an element of clause is known to be false, remove it
					if elem == -unitClause:
						removeFromCounter(elem)
						del clauses[idx1][idx2]
						removed = 1
					#if an element of clause is known to be true, remove clause
					if elem == unitClause:
						removeFromCounter(clause)
						del clauses[idx1]
						removed = 1
						break
	except Exception as e:
		print(e)
		return clauses, truthValues, removed
	return clauses, truthValues, removed


def checkPurity(clauses, truthValues):
	for elem in elemCounter:
		if elemCounter[elem] > 0 and elemCounter[-elem] == 0:
			if elem>0:
				truthValues[abs(elem)] = 1
			else:
				truthValues[abs(elem)] = 0

#@timeit
def solveDp(clauses, truthValues):
	'''
	Given a set of rules, (sudoku rules + puzzle)
	find a solution and return it. 
	Uses DP algorithm
	'''

	#Check termination conditions
	if not clauses:
		return clauses,truthValues,'SAT'

	#Simplify clauses as much as possible
	removed = 1
	while removed:
		removed = 0
		clauses, removed = removeTautology(clauses)
		checkPurity(clauses, truthValues)
		clauses, truthValues, removed = removeUnitClauses(clauses, truthValues)
		#If clause contains false element, remove element (since it doesn't affect the clause's value)
		#If clause contains true element, remove clause (since it's true regardless)
		#check purity

		break
	if [] in clauses:
		return clauses,truthValues,'UNSAT'
	if not clauses:
		return clauses,truthValues,"SAT"
	return clauses, truthValues, 0
	#Backtrack boys
	#TODO


if __name__ == "__main__":
	
	sudokuRules = getRules()
	games = readGames(r'test sudokus/1000 sudokus.txt')
	game1 = sudokuRules + games[0]
	print(len(game1))
	elemCounter = Counter(list(chain(*game1)))
	newClauses, truthVals, sat = solveDp(game1,{})
	#print(newClauses)
	print('Length of clauses after removal:',len(newClauses))
	#split + backtrack
	# split=0
	# presplitClauses=copy.deepcopy(newClauses)
	# presplitTruthVals=truthVals.copy()
	# presplitCounter=copy.deepcopy(elemCounter)
	# while True:
	# 	print(sat)
	# 	if sat=="UNSAT":
	# 		newClauses=copy.deepcopy(presplitClauses)
	# 		truthVals=presplitTruthVals.copy()
	# 		truthVals[split]=0
	# 		elemCounter=copy.deepcopy(presplitCounter)
	# 	elif sat==0:
	# 		presplitClauses=copy.deepcopy(newClauses)
	# 		presplitTruthVals=truthVals.copy()
	# 		presplitCounter=copy.deepcopy(elemCounter)
	# 	elif sat=="SAT":
	# 		answer=[k for k,v in truthVals.items() if v == 1 and k>0]
	# 		print(answer)
	# 		print(len(answer))
	# 		break
	# 	while True:
	# 		clause=newClauses[random.randint(0,len(newClauses)-1)]
	# 		#print(newClauses)
	# 		split=clause[random.randint(0,len(clause)-1)]
	# 		splitCell=split//10
	# 		truthCells=[k//10 for k,v in truthVals.items() if v==1 and k>0]
	# 		#print('Filled Squares:',sorted([k for k,v in truthVals.items() if v==1 and k>0]))
	# 		if splitCell not in truthCells:
	# 			break
	# 	truthVals[split]=1
	# 	truthVals[split]=0
	# 	newClauses, truthVals,sat = solveDp(newClauses,truthVals)
		# print('Length of clauses after removal:',len(newClauses))
		#print(truthVals)