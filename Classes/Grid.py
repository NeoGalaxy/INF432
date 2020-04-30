import io
from itertools import groupby as gb

class Direction:
	NORD = 0
	SUD = 1
	EST = 2
	OUEST = 3
(NORD, SUD, EST, OUEST) = (Direction.NORD, Direction.SUD, Direction.EST, Direction.OUEST)

class Grid:

	groups = []
	def __init__(self, arg):
		self.__l = 0
		self.__h = 0
		self.__barrier  = {'v':[], 'h':[]} # AKA. Bc and Bl in the report
		self.__values = {'v':[], 'h':[]} # AKA. Zc and Zl in the report
		self.__groups = None
		self.__waterPhysicsCNF =  CNF() #déclaration d'un CNF vide
		self.barrier = self.__barrier
		self.values = self.__values

		try:
			if (type(arg) == io.TextIOWrapper) :
				grid = arg.read().split("\n")
			elif (type(arg) == str) :
				if ('\n' in arg) :
					grid = arg.split("\n")
				else :
					f = open(arg, "r")
					grid = f.read().split("\n")
					f.close()
				
			elif (type(arg) == list) :
				grid = arg
			else :
				raise TypeError("The argument should be a string containing the grid, a list of strings, each being a line of the grid, a string containing a file's name or directly the file.")
		except Exception as e:
			raise e

		if grid[0] == "grid1":
			self.__readGrid(grid[1:])
		else :
			raise ValueError("Invalid format (the first line '"+grid[0]+"' does not correspond to grid1).\n")

		self.__createWaterPhysic()

	def mkGroups(self) :
		nbGroups = 0
		self.__groups = [[None for i in range(self.__l)] for j in range(self.__h)]
		for i in range(self.__l):
			for j in range(self.__h):
				if (self.__groups[j][i] == None):
					nbGroups += 1
					self.__addToGrp(i,j,nbGroups)

		return self #-> allow to do: grille = Grid(arg).mkGroups()

	def getBarrier(self,i,j,o):
		if not(0 <= i < self.__l) or not(0 <= j < self.__h) : # Yes, it is allowed in python xD
			raise KeyError("The node of coordinates ("+str(i)+","+str(j)+") doesn't exist.")

		if (o == NORD) :
			if (j == self.__h-1) : return True # The first line always have a barrier above
			return (self.__barrier["h"][self.__h-2-j][i])

		if (o == SUD) :
			if (j == 0) : return True # The last line always have a barrier under
			return (self.__barrier["h"][self.__h-1-j][i])
			
		if (o == EST) :
			if (i == self.__l -1) : return True # The line on the left always have a barrier on its left
			return (self.__barrier["v"][self.__h-1-j][i])
			
		if (o == OUEST) :
			if (i == 0) : return True # The line on the right always have a barrier on its right
			return (self.__barrier["v"][self.__h-1-j][i-1])
			
				
	def getGrid(self):
		res = "grid\n  " + ("_ " * self.__l) + "\n"
		for y in range(self.__h):
			res += str(self.__values['h'][y]) if self.__values['h'][y] != -1 else " "
			res += '|'
			for x in range(self.__l):
				res += '_' if y == self.__h-1 or self.__barrier['h'][y][x] else ' '
				res += '|' if x == self.__l-1 or self.__barrier['v'][y][x] else ' '
			res += "\n"
		res += "  " + " ".join(str(x) if x != -1 else " " for x in self.__values['v'])
		return res

	###################### Private methods ######################

	def __readGrid(self, textLines):
		colsIndex = None
		for line in textLines:
			line = line.split("#",1)[0]    # We don't take in account the comments
			if len(line) == 0: continue  # If the line is empty, we can skip it

			"""Parse the first line"""
			if colsIndex == None:
				colsIndex = [(0,len(line.split("_",1)[0])-1)] # give the width of the first column of the lines
				if line[0] != " " : 
					raise ValueError("The first line should start with white spaces.")
				for char, nb in ((label, sum(1 for _ in group)) for label, group in gb(line)):
					if not char in " _":
						raise ValueError("The first line should only contain white spaces and underscores.")
					if char == " " and nb > 1 and len(colsIndex) > 1:
						raise ValueError("The column separator between col "+str(len(colsIndex)-1)+" and col "+str(len(colsIndex))+" is too wide.")
					if char == "_":
						colsIndex.append(((colsIndex[-1][1]+1), (nb+colsIndex[-1][1]+1)))
				self.__l = len(colsIndex)-1
				continue

			"""Prepare the parsing of other lines"""
			"""try:
				splitted_line = [line[x:y] for x,y in colsIndex]
			except Exception as e:
				raise e"""

			"""Parse the last line"""
			if line[colsIndex[0][1]] != "|": 
				self.__values["v"] = [self.__strToVal(line[x:y],len(self.__barrier["v"])) for x,y in colsIndex[1:]]

				"""Parse all the other lines"""
			else : 
				barrier = {"v":[], "h":[]}
				self.__values["h"].append(self.__strToVal(line[0:colsIndex[0][1]], len(colsIndex)-1))
				for x,y in colsIndex[1:] :
					s = line[x:y]
					if not (s[0] in " _") or len(list(gb(s))) > 1 :
						raise ValueError("La grille a une erreur ligne "+str(len(self.__values["h"])))

					if s[0] == '_':
						barrier["h"].append(True)
					else :
						barrier["h"].append(False)

					if line[y] == '|':
						barrier["v"].append(True)
					else :
						barrier["v"].append(False)

				self.__barrier["h"].append(barrier["h"])
				barrier["v"].pop()
				self.__barrier["v"].append(barrier["v"])

		self.__barrier["h"].pop()
		self.__h = len(self.__barrier["v"])

	def __addToGrp(self,i,j,n):
		self.__groups[j][i] = n
		self.groups = self.__groups
		if (not(self.getBarrier(i,self.__h-1-j, SUD)) and self.__groups[j+1][i] == None): 
			self.__addToGrp(i,j+1,n)

		if (not(self.getBarrier(i,self.__h-1-j, NORD)) and self.__groups[j-1][i] == None): 
			self.__addToGrp(i,j-1,n)

		if (not(self.getBarrier(i,self.__h-1-j, EST)) and self.__groups[j][i+1] == None): 
			self.__addToGrp(i+1,j,n)

		if (not(self.getBarrier(i,self.__h-1-j, OUEST)) and self.__groups[j][i-1] == None): 
			self.__addToGrp(i-1,j,n)
	
	def __strToVal(self, elem, s) :
		elem = elem.strip()
		if elem == "":
			return -1
		if elem.isdigit():
			elem = int(elem)
			if not(0 <= elem <= s):
				raise ValueError("The values should be between 0 and the size. "+str(elem)+" is not in these bounds.")
			return elem
		else:
			raise ValueError("The last line should contain only digits and spaces.")

	def __createWaterPhysic(self) :
		a,b,x,y = 0,0,0,0
		for a in range (0, self.__l):
			for b in range (0, self.__h):
				for x in range (0, self.__l):
					for y in range(0, b+1):
						if (self.__groups[a][b] == self.__groups[x][y]) :
							self.__waterPhysicsCNF.addClause("-"+str(a)+","+str(b) , str(x)+","+str(y))

	def __str__(self):
		return "("+str(self.__l)+"x"+str(self.__h)+" grid)"

	def __repr__(self):
		return self.__str__()

