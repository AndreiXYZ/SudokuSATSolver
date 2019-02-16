import copy
from collections import Counter
import time

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
	truthValuesAll = []
	with open(file, 'r') as f:
		for game in f:
			truthValues, gameRules = gameToCnf(game)
			games.append(gameRules)
			truthValuesAll.append(truthValues)
	return games


def gameToCnf(gameString):
	#Converts game string to CNF rules.
	#Squares that are filled in are an extra constraint
	gameRules = []
	truthValues = dict()
	for idx, elem in enumerate(gameString):
		if elem not in ['.', '\n']:
			row = idx//9+1
			col = idx%9+1
			val = row*100+col*10+int(elem)
			gameRules.append([val])
			truthValues[val] = 1
	return truthValues, gameRules

def removeTautology(clauses):
	removed = 0
	clauses = [x for x in clauses if not(len(x)==2 and x[0]==-x[1])]
	try:
		for i in range(len(clauses)):
			if len(clauses[i]) == 2 and x[0]==-x[1]:
				del clauses[i]
				removed = 1
	except:
		return clauses, removed
	return clauses, removed

def removeUnitClauses(clauses, truthValues):
	removed = 0
	try:
		for i in range(len(clauses)):
				if len(clauses[i])==1:
					if clauses[i][0] > 0:
						truthValues[clauses[i][0]] = 1
					else:
						truthValues[clauses[i][0]] = 0
					del clauses[i]
					removed = 1
	except:
		return clauses, truthValues, removed
	return clauses, truthValues, removed

def removePurity(clauses, truthValues):
	removed = 0
	for i in range(len(clauses)):
		for elem in range(len(clauses[i])):
			pass

@timeit
def solveDp(clauses, truthValues):
	'''
	Given a set of rules, (sudoku rules + puzzle)
	find a solution and return it. 
	Uses DP algorithm
	'''

	#Check termination conditions
	if not clauses:
		return 'SAT'
	if [] in clauses:
		return 'UNSAT'

	#Simplify clauses as much as possible
	removed = 1
	while removed:
		removed = 0
		elemCounter.clear()
		clauses, removed = removeTautology(clauses)
		clauses, truthValues, removed = removeUnitClauses(clauses, truthValues)
		#If clause contains false element, remove element (since it doesn't affect the clause's value)
		#If clause contains true element, remove clause (since it's true regardless)
		for clause in clauses:
			for elem in clause:
				elemCounter[elem] += 1
				try:
					if truthValues.get(elem) == 1:
						clauses.remove(clause)
						# print('clause removed: ', clause)
						removed = 1
					if truthValues.get(elem) == 0:
						clauses[clauses.index(clause)].remove(elem)
				except:
					pass
				finally:
					#check purity
					if elemCounter[elem] > 0 and elemCounter[-elem] == 0:
						if elem>0:
							truthValues[elem] = 1
						else:
							truthValues[elem] = 0
						removed = 1

	if not clauses:
		print('SAT')
	return clauses, truthValues
	#Backtrack boys
	#TODO

if __name__ == "__main__":
	sudokuRules = getRules()
	games = readGames(r'test sudokus/1000 sudokus.txt')
	game1 = sudokuRules + games[0]
	elemCounter = Counter()
	newClauses, truthVals = solveDp(game1,{})
	print('Length of clauses after removal:',len(newClauses))
	print('Game length:',len(games[0]))