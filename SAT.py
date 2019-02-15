import copy

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
			games.append(gameToCnf(game))
	return games


def gameToCnf(gameString):
	#Converts game string to CNF rules.
	#Squars that are filled in are an extra constraint
	gameRules = []
	truthValues = dict()
	for idx, elem in enumerate(gameString):
		if elem not in ['.', '\n']:
			gameRules.append([idx//9+1, idx%9+1, int(elem)])
			truthValues[elem] = 1
	return gameRules


def solveDp(clauses, truthValues):
	'''
	Given a set of rules, (sudoku rules + puzzle)
	find a solution and return it. 
	Uses DP algorithm
	'''
	
	#check termination conditions
	if not clauses:
		return 'SAT'
	if [] in clauses:
		return 'UNSAT'

	#Simplify clauses
	for clause in clauses:
		
		#check tautology
		if len(clause==2):
			if clause[0] == -clause[1]:
				clauses.remove(clause)
		#check unit clause
		if len(clause==1):
			elem = clause[0]
			truthValues[elem] = (1,0)[elem<0]
			clauses.remove(clause)
		#check purity
		#TODO



if __name__ == "__main__":
	sudokuRules = getRules()
	games = readGames('test sudokus/1000 sudokus.txt')

	game1 = sudokuRules + games[0]
	