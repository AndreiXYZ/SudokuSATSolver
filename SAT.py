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
            start_time = time.clock()
            is_evaluating = True
            try:
                value = f(*args)
            finally:
                is_evaluating = False
            end_time = time.clock()
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

	#If clause contains false element, remove element (since it doesn't affect the clause's value)
	#If clause contains true element, remove clause (since it's true regardless)
	for idx1, clause in enumerate(clauses):
		for elem in enumerate(clause):
			if truthValues.get(elem) == 1:
				clauses.remove(clause)
			if truthValues.get(elem) == 0:
				clauses[idx1].remove(elem)
	
	#Simplify clauses as much as possible
	done = 0
	while not done:
		done = 1
		for clause in clauses:
			#check tautology
			if len(clause)==2:
				if clause[0] == -clause[1]:
					done = 0
					clauses.remove(clause)
					print('clause removed: ', clause)
			#check unit clause
			if len(clause)==1:
				done = 0
				if clause[0] > 0:
					truthValues[clause[0]] = 1
				else:
					truthValues[clause[0]] = 0
				clauses.remove(clause)
				print('clause removed: ', clause)
			#check purity
			#TODO
			#maybe use a counter

	return clauses, truthValues
	#Backtrack boys
	#TODO

if __name__ == "__main__":
	sudokuRules = getRules()
	games = readGames('test sudokus/1000 sudokus.txt')
	game1 = sudokuRules + games[0]
	newClauses, newTruthVals = solveDp(game1,{})