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
	code = 0
	valuetbl = [0]
	init_value = piece_values[code]

	def __init__(self, pos, col):
		self.position = pos
		self.color = col
		# update value, cant use method because we need position
		if self.color == Color.WHITE:
			self.value = self.init_value + self.valuetbl[self.position]
		else:
			self.value = self.init_value + self.valuetbl[self.flip_index_table[self.position]]
		self.moveList = []

	def __str__(self):
		if self.color == Color.WHITE:
			return piece_str[self.code] 
		else:
			return piece_str[self.code].lower()
	
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
		self.moveList.append(self)
		# clean capture
		if tosq in self.attackSquares(current):
			self.position = tosq
			self.updateValue(current)
		else:
			raise IllegalMoveException()

class Pawn(Piece):
	code = 0
	valuetbl = [
		0,  0,  0,  0,  0,  0,  0,  0,
		50,50, 50, 50, 50, 50, 50, 50,
		10,10, 20, 30, 30, 20, 10, 10,
		5,  5, 10, 25, 25, 10,  5,  5,
		0,  0,  0, 20, 20,  0,  0,  0,
		5, -5,-10,  0,  0,-10, -5,  5,
		5, 10, 10,-20,-20, 10, 10,  5,
		0,  0,  0,  0,  0,  0,  0,  0]

	# TODO promotion and so on
	def attackSquares(self, current):
		validMoves = []
		caps = []
		if self.color == Color.WHITE:
			forward = self.position - 8
			double = self.position - 16
			cap = [self.position - 9, self.position - 7]
			if self.position > 47:
				if not(current.board[double]) and not(current.board[double]):
					# append double step
					validMoves.append(double)
		else:
			forward = self.position + 8
			double = self.position + 16
			cap = [self.position + 9, self.position + 7]
			if self.position < 16:
				if not(current.board[forward]) and not(current.board[double]):
					# append double step
					validMoves.append(double)
				
		# single step
		if mailbox[mailbox64[forward]] and not(current.board[forward]):
			validMoves.append(forward)
		# captures
		for m in caps:
			if mailbox[mailbox64[m]] and current.board[m]:
				validMoves.append(m)
		return validMoves

class Knight(Piece):
	code = 1
	valuetbl = [
		-50,-40,-30,-30,-30,-30,-40,-50,
		-40,-20,  0,  0,  0,  0,-20,-40,
		-30,  0, 10, 15, 15, 10,  0,-30,
		-30,  5, 15, 20, 20, 15,  5,-30,
		-30,  0, 15, 20, 20, 15,  0,-30,
		-30,  5, 10, 15, 15, 10,  5,-30,
		-40,-20,  0,  5,  5,  0,-20,-40,
		-50,-40,-30,-30,-30,-30,-40,-50]

	def attackSquares(self, current):
		validMoves = []
		knightmoves = [-21, -19, -8, 12, 21, 19, 8, -12]
		for move in knightmoves:
			# field is in bounds
			if mailbox[mailbox64[self.position] + move] > 0:
				# field is not empty
				if (current.board[mailbox[mailbox64[self.position] + move]]):
					if current.board[mailbox[mailbox64[self.position] + move]].color != self.color:
						validMoves.append(mailbox[mailbox64[self.position] + move])
				# field is empty
				else:
					validMoves.append(mailbox[mailbox64[self.position] + move])
		return validMoves
	
class Bishop(Piece):
	code = 2
	valuetbl= [
		-20,-10,-10,-10,-10,-10,-10,-20,
		-10,  0,  0,  0,  0,  0,  0,-10,
		-10,  0,  5, 10, 10,  5,  0,-10,
		-10,  5,  5, 10, 10,  5,  5,-10,
		-10,  0, 10, 10, 10, 10,  0,-10,
		-10, 10, 10, 10, 10, 10, 10,-10,
		-10,  5,  0,  0,  0,  0,  5,-10,
		-20,-10,-10,-10,-10,-10,-10,-20]

	def attackSquares(self, current):
		validMoves = []
		count = 1
		iterate = [True, True, True, True]
		# while at least one direction to move in
		while True in iterate:
			mIndex = mailbox64[self.position]
			# indices for north, east, south and west
			indexList = [mIndex - count*9, mIndex + count*11, mIndex + count*9, mIndex - count*11]
			# check if we are out of bounds N, E, S or W
			for directionIndex,i in enumerate(indexList):
				if (iterate[directionIndex] and mailbox[i] > 0):
					# if theres a piece on the square
					if (current.board[mailbox[i]]):
						# we cant move further
						iterate[directionIndex] = False
						# if color is other color
						if (current.board[mailbox[i]].color != self.color):
							# we can capture
							validMoves.append(mailbox[i])
					# otherwise we can move there
					else:
						validMoves.append(mailbox[i])
				else: iterate[directionIndex] = False
			count += 1
		return validMoves

class Rook(Piece):
	code = 3
	valuetbl = [
		 0,  0,  0,  0,  0,  0,  0,  0,
		 5, 10, 10, 10, 10, 10, 10,  5,
		-5,  0,  0,  0,  0,  0,  0, -5,
		-5,  0,  0,  0,  0,  0,  0, -5,
		-5,  0,  0,  0,  0,  0,  0, -5,
		-5,  0,  0,  0,  0,  0,  0, -5,
		-5,  0,  0,  0,  0,  0,  0, -5,
		 0,  0,  0,  5,  5,  0,  0,  0]

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
			mIndex = mailbox64[self.position]
			# indices for north, east, south and west
			indexList = [mIndex - count*10, mIndex + count, mIndex + count*10, mIndex - count]
			# check if we are out of bounds N, E, S or W
			for directionIndex,i in enumerate(indexList):
				if (iterate[directionIndex] and mailbox[i] > 0):
					# if theres a piece on the square
					if current.board[mailbox[i]]:
						# we cant move further
						iterate[directionIndex] = False
						# if color is other color
						if (current.board[mailbox[i]].color != self.color):
							# we can capture
							validMoves.append(mailbox[i])
					# otherwise we can move there
					else:
						validMoves.append(mailbox[i])
				else: iterate[directionIndex] = False
			count += 1
		return validMoves

class Queen(Piece):
	code = 4
	valuetbl= [
		-20,-10,-10, -5, -5,-10,-10,-20,
		-10,  0,  0,  0,  0,  0,  0,-10,
		-10,  0,  5,  5,  5,  5,  0,-10,
		 -5,  0,  5,  5,  5,  5,  0, -5,
		  0,  0,  5,  5,  5,  5,  0, -5,
		-10,  5,  5,  5,  5,  5,  0,-10,
		-10,  0,  5,  0,  0,  0,  0,-10,
		-20,-10,-10, -5, -5,-10,-10,-20]

	def attackSquares(self, current):
		# queens attack squares are rook U bishop
		# they dont have any squares in common
		# so we can just merge the lists and dont need to check for duplicates
		b = Bishop(self.position, self.color)
		r = Rook(self.position, self.color)
		validMoves = b.attackSquares(current) + r.attackSquares(current)
		print(validMoves)
		# clean up the waste
		del b
		del r
		return validMoves

class King(Piece):
	code = 5
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

	def updateValue(self, current):
		if self.color == Color.WHITE:
			pos = self.position
		else:
			pos = self.flip_index_table[self.position]
		# make value depending on state of the game
		self.value = self.tbl_king_end[pos] * (current.gameIndex) + self.valuetbl[pos] * (1 -current.gameIndex)

	def attackSquares(self, current):
		validMoves = []
		kingmoves = [1,11,10,9,-1,-11,-10,-9]
		# TODO: check checks (hihi), castling
		for move in kingmoves:
			if mailbox[mailbox64[self.position] + move] >= 0 \
				and not(self.inCheck(mailbox[mailbox64[self.position] + move], current)):
				if current.board[mailbox[mailbox64[self.position] + move]]:
					if current.board[mailbox[mailbox64[self.position] + move]].color != self.color:
						validMoves.append(mailbox[mailbox64[self.position] + move])
				else:
					validMoves.append(mailbox[mailbox64[self.position] + move])
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

