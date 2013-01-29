from defs import *

# TODO clear distincition between boards movePiece
# and pieces' moveTo methods

class Piece(object):
	flip_index_table = [
		56, 57, 58, 59, 60, 61, 62, 63,
		48, 49, 50, 51, 52, 53, 54, 55,
		40, 41, 42, 43, 44, 45, 46, 47,
		32, 33, 34, 35, 36, 37, 38, 39,
		24, 25, 26, 27, 28, 29, 30, 31,
		16, 17, 18, 19, 20, 21, 22, 23,
		8,  9,  10, 11, 12, 13, 14, 15,
		0,  1,   2,  3,  4,  5,  6,  7]
	valuetbl = [0]

	def __int__(self):
		return -1

	def __init__(self, pos, col):
		self.init_value = PIECE_VALUES[int(self)]
		self.position = pos
		self.color = col
		# update value
		if self.color == Color.WHITE:
			self.value = self.init_value + self.valuetbl[self.position]
		else:
			self.value = self.init_value + self.valuetbl[self.flip_index_table[self.position]]
		self.moveList = []

	def __str__(self):
		if self.color == Color.WHITE:
			return PIECE_STR[int(self)] 
		else:
			return PIECE_STR[int(self)].lower()
	
	def __cmp__(self, other):
		if self.value == other.value:
			return 0
		if self.value > other.value:
			return 1
		if self.value < other.value:
			return -1

	# array of squares attacked by the piece
	def attackSquares(self, current):
		pass
	
	def updateValue(self, current):
		if self.color == Color.WHITE:
			self.value = self.init_value + self.valuetbl[self.position]
		else:
			self.value = self.init_value + self.valuetbl[self.flip_index_table[self.position]]

	def moveTo(self, tosq, current):
		# clean capture
		if tosq in self.attackSquares(current):
			self.position = tosq
			self.updateValue(current)
			self.moveList.append(self)
			return True
		else:
			return False

class Pawn(Piece):
	valuetbl = [
		0,  0,  0,  0,  0,  0,  0,  0,
		50,50, 50, 50, 50, 50, 50, 50,
		10,10, 20, 30, 30, 20, 10, 10,
		5,  5, 10, 25, 25, 10,  5,  5,
		0,  0,  0, 20, 20,  0,  0,  0,
		5, -5,-10,  0,  0,-10, -5,  5,
		5, 10, 10,-20,-20, 10, 10,  5,
		0,  0,  0,  0,  0,  0,  0,  0]

	def __int__(self):
		return 0

	# TODO promotion and so on
	def attackSquares(self, current):
		validMoves = []
		caps = []
		if self.color == Color.WHITE:
			forward = MAILBOX64[self.position] - 10
			double = self.position - 16
			caps = [MAILBOX64[self.position] - 11, MAILBOX64[self.position] - 9]
			if self.position > 47:
				if not(current.board[double]) and not(current.board[MAILBOX[forward]]):
					# append double step
					validMoves.append(double)
		else:
			forward = MAILBOX64[self.position] + 10
			double = self.position + 16
			caps = [MAILBOX64[self.position] + 11, MAILBOX64[self.position] + 9]
			if self.position < 16:
				if not(current.board[double]) and not(current.board[MAILBOX[forward]]):
					# append double step
					validMoves.append(double)
				
		# single step
		if MAILBOX[forward] >= 0 and not(current.board[MAILBOX[forward]]):
			validMoves.append(MAILBOX[forward])
		# captures
		for m in caps:
			if MAILBOX[m] >= 0 and current.board[MAILBOX[m]]:
				validMoves.append(MAILBOX[m])
		return validMoves

class Knight(Piece):
	valuetbl = [
		-50,-40,-30,-30,-30,-30,-40,-50,
		-40,-20,  0,  0,  0,  0,-20,-40,
		-30,  0, 10, 15, 15, 10,  0,-30,
		-30,  5, 15, 20, 20, 15,  5,-30,
		-30,  0, 15, 20, 20, 15,  0,-30,
		-30,  5, 10, 15, 15, 10,  5,-30,
		-40,-20,  0,  5,  5,  0,-20,-40,
		-50,-40,-30,-30,-30,-30,-40,-50]

	def __int__(self):
		return 1

	def attackSquares(self, current):
		validMoves = []
		knightmoves = [-21, -19, -8, 12, 21, 19, 8, -12]
		for move in knightmoves:
			# field is in bounds
			if MAILBOX[MAILBOX64[self.position] + move] >= 0:
				# field is not empty
				if (current.board[MAILBOX[MAILBOX64[self.position] + move]]):
					if current.board[MAILBOX[MAILBOX64[self.position] + move]].color != self.color:
						validMoves.append(MAILBOX[MAILBOX64[self.position] + move])
				# field is empty
				else:
					validMoves.append(MAILBOX[MAILBOX64[self.position] + move])
		return validMoves
	
class Bishop(Piece):
	valuetbl= [
		-20,-10,-10,-10,-10,-10,-10,-20,
		-10,  0,  0,  0,  0,  0,  0,-10,
		-10,  0,  5, 10, 10,  5,  0,-10,
		-10,  5,  5, 10, 10,  5,  5,-10,
		-10,  0, 10, 10, 10, 10,  0,-10,
		-10, 10, 10, 10, 10, 10, 10,-10,
		-10,  5,  0,  0,  0,  0,  5,-10,
		-20,-10,-10,-10,-10,-10,-10,-20]

	def __int__(self):
		return 2

	def attackSquares(self, current):
		validMoves = []
		count = 1
		iterate = [True, True, True, True]
		# while at least one direction to move in
		while True in iterate:
			mIndex = MAILBOX64[self.position]
			# indices for north, east, south and west
			indexList = [mIndex - count*9, mIndex + count*11, mIndex + count*9, mIndex - count*11]
			# check if we are out of bounds N, E, S or W
			for directionIndex,i in enumerate(indexList):
				if iterate[directionIndex] and MAILBOX[i] >= 0:
					# if theres a piece on the square
					if (current.board[MAILBOX[i]]):
						# we cant move further
						iterate[directionIndex] = False
						# if color is other color
						if (current.board[MAILBOX[i]].color != self.color):
							# we can capture
							validMoves.append(MAILBOX[i])
					# otherwise we can move there
					else:
						validMoves.append(MAILBOX[i])
				else: iterate[directionIndex] = False
			count += 1
		return validMoves

class Rook(Piece):
	valuetbl = [
		 0,  0,  0,  0,  0,  0,  0,  0,
		 5, 10, 10, 10, 10, 10, 10,  5,
		-5,  0,  0,  0,  0,  0,  0, -5,
		-5,  0,  0,  0,  0,  0,  0, -5,
		-5,  0,  0,  0,  0,  0,  0, -5,
		-5,  0,  0,  0,  0,  0,  0, -5,
		-5,  0,  0,  0,  0,  0,  0, -5,
		 0,  0,  0,  5,  5,  0,  0,  0]

	def __int__(self):
		return 3

	def __str__(self):
		if self.color == Color.WHITE:
			return "R"
		else:
			return "r"

	def attackSquares(self, current):
		validMoves = []
		count = 1
		iterate = [True, True, True, True]
		# while at least one direction to move in
		while True in iterate:
			mIndex = MAILBOX64[self.position]
			# indices for north, east, south and west
			indexList = [mIndex - count*10, mIndex + count, mIndex + count*10, mIndex - count]
			# check if we are out of bounds N, E, S or W
			for directionIndex,i in enumerate(indexList):
				if iterate[directionIndex] and MAILBOX[i] >= 0:
					# if theres a piece on the square
					if current.board[MAILBOX[i]]:
						# we cant move further
						iterate[directionIndex] = False
						# if color is other color
						if current.board[MAILBOX[i]].color != self.color:
							# we can capture
							validMoves.append(MAILBOX[i])
					# otherwise we can move there
					else:
						validMoves.append(MAILBOX[i])
				else: iterate[directionIndex] = False
			count += 1
		return validMoves

class Queen(Piece):
	valuetbl= [
		-20,-10,-10, -5, -5,-10,-10,-20,
		-10,  0,  0,  0,  0,  0,  0,-10,
		-10,  0,  5,  5,  5,  5,  0,-10,
		 -5,  0,  5,  5,  5,  5,  0, -5,
		  0,  0,  5,  5,  5,  5,  0, -5,
		-10,  5,  5,  5,  5,  5,  0,-10,
		-10,  0,  5,  0,  0,  0,  0,-10,
		-20,-10,-10, -5, -5,-10,-10,-20]

	def __int__(self):
		return 4

	def attackSquares(self, current):
		validMoves = []
		count = 1
		iterate = [True for i in range(8)]
		# while at least one direction to move in
		while True in iterate:
			mIndex = MAILBOX64[self.position]
			# indices for north, east, south and west
			indexList = [mIndex - count*10, mIndex + count, mIndex + count*10, mIndex - count]
			indexList += [mIndex - count*9, mIndex + count*11, mIndex + count*9, mIndex - count*11]
			# check if we are out of bounds N, E, S or W
			for directionIndex,i in enumerate(indexList):
				if iterate[directionIndex] and MAILBOX[i] >= 0:
					# if theres a piece on the square
					if current.board[MAILBOX[i]]:
						# we cant move further
						iterate[directionIndex] = False
						# if color is other color
						if current.board[MAILBOX[i]].color != self.color:
							# we can capture
							validMoves.append(MAILBOX[i])
					# otherwise we can move there
					else:
						validMoves.append(MAILBOX[i])
				else: iterate[directionIndex] = False
			count += 1
		return validMoves

class King(Piece):
	valuetbl = [
		-30,-40,-40,-50,-50,-40,-40,-30,
		-30,-40,-40,-50,-50,-40,-40,-30,
		-30,-40,-40,-50,-50,-40,-40,-30,
		-30,-40,-40,-50,-50,-40,-40,-30,
		-20,-30,-30,-40,-40,-30,-30,-20,
		-10,-20,-20,-20,-20,-20,-20,-10,
		 20, 20,  0,  0,  0,  0, 20, 20,
		 20, 30, 10,  0,  0, 10, 30, 20]
	tbl_king_end = [
		-50,-40,-30,-20,-20,-30,-40,-50,
		-30,-20,-10,  0,  0,-10,-20,-30,
		-30,-10, 20, 30, 30, 20,-10,-30,
		-30,-10, 30, 40, 40, 30,-10,-30,
		-30,-10, 30, 40, 40, 30,-10,-30,
		-30,-10, 20, 30, 30, 20,-10,-30,
		-30,-30,  0,  0,  0,  0,-30,-30,
		-50,-30,-30,-30,-30,-30,-30,-50]

	def __int__(self):
		return 5

	def attackSquares(self, current):
		validMoves = []
		kingmoves = [1,11,10,9,-1,-11,-10,-9]
		# TODO: check checks (hihi)
		for move in kingmoves:
			if MAILBOX[MAILBOX64[self.position] + move] >= 0 \
				and not(self.inCheck(MAILBOX[MAILBOX64[self.position] + move], current)):
				if current.board[MAILBOX[MAILBOX64[self.position] + move]]:
					if current.board[MAILBOX[MAILBOX64[self.position] + move]].color != self.color:
						validMoves.append(MAILBOX[MAILBOX64[self.position] + move])
				else:
					validMoves.append(MAILBOX[MAILBOX64[self.position] + move])
		return validMoves

	def inCheck(self, pos, current):
		for i in range(64):
			thispiece = current.board[i]
			# TODO continue here, check that iterated piece is not king itself
			if thispiece and not(isinstance(thispiece,King)):
				if thispiece.color != self.color and pos in thispiece.attackSquares(current):
					return True
		else:
			return False
