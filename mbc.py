from copy import deepcopy
from sys import exit

# TODO clear distincition between boards movePiece
# and pieces' moveTo methods

# mailbox representation to check validity of moves
mailbox = [
	-1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
	-1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
	-1,  0,  1,  2,  3,  4,  5,  6,  7, -1,
	-1,  8,  9, 10, 11, 12, 13, 14, 15, -1,
	-1, 16, 17, 18, 19, 20, 21, 22, 23, -1,
	-1, 24, 25, 26, 27, 28, 29, 30, 31, -1,
	-1, 32, 33, 34, 35, 36, 37, 38, 39, -1,
	-1, 40, 41, 42, 43, 44, 45, 46, 47, -1,
	-1, 48, 49, 50, 51, 52, 53, 54, 55, -1,
	-1, 56, 57, 58, 59, 60, 61, 62, 63, -1,
	-1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
	-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]

# mailbox 64 to translate positions to mailbox layout
mailbox64 = [
	21, 22, 23, 24, 25, 26, 27, 28,
	31, 32, 33, 34, 35, 36, 37, 38,
	41, 42, 43, 44, 45, 46, 47, 48,
	51, 52, 53, 54, 55, 56, 57, 58,
	61, 62, 63, 64, 65, 66, 67, 68,
	71, 72, 73, 74, 75, 76, 77, 78,
	81, 82, 83, 84, 85, 86, 87, 88,
	91, 92, 93, 94, 95, 96, 97, 98]

# notation for easily translating
notation = [
	"a8","b8","c8","d8","e8","f8","g8","h8",
	"a7","b7","c7","d7","e7","f7","g7","h7",
	"a6","b6","c6","d6","e6","f6","g6","h6",
	"a5","b5","c5","d5","e5","f5","g5","h5",
	"a4","b4","c4","d4","e4","f4","g4","h4",
	"a3","b3","c3","d3","e3","f3","g3","h3",
	"a2","b2","c2","d2","e2","f2","g2","h2",
	"a1","b1","c1","d1","e1","f1","g1","h1"]

# for the board printer
piece_str = 'PNBRQK'
# lookup initial piece values
piece_values = [100, 325, 325, 500, 975, 20000]

class Color(object):
	WHITE = 0
	BLACK = 1

class IllegalMoveException(Exception):
	pass

class Position(object):
	def __init__(self):
		# -1 == no en passant square
		self.epSquare = -1
		# white queenside, white kingside, black queenside, black kingside
		self.castlingRights = [True,True,True,True]
		self.moveList = []
		# index is 1 in endgame
		self.gameIndex = 0
		# TODO update this every move
		self.currentEval = [1505,1505]
		self.board = [
			Rook(0,Color.BLACK),
			Knight(1,Color.BLACK),
			Bishop(2,Color.BLACK),
			Queen(3,Color.BLACK),
			King(4,Color.BLACK),
			Bishop(5,Color.BLACK),
			Knight(6,Color.BLACK),
			Rook(7,Color.BLACK)]
		self.board += [Pawn(i, Color.BLACK) for i in range(8,16)]
		self.board += [None for x in range(16,48)]
		self.board += [Pawn(i, Color.WHITE) for i in range(48,56)]
		self.board += [
			Rook(56,Color.WHITE),
			Knight(57,Color.WHITE),
			Bishop(58,Color.WHITE),
			Queen(59,Color.WHITE),
			King(60,Color.WHITE),
			Bishop(61,Color.WHITE),
			Knight(62,Color.WHITE),
			Rook(63,Color.WHITE)]

	def __str__(self):
		dottedLine = "+---+---+---+---+---+---+---+---+"
		enumeration = [str(n) + " " for n in range(8,0,-1)]
		s = ""
		for i in range(64):
			if i % 8 == 0:
				s += "\n"
				s += "  " + dottedLine + "\n"
				s += enumeration[i//8]
				s += "| "
			if self.board[i]:
				s += str(self.board[i])
			elif (i % 2 != i//8 % 2):
				s += "."
			else:
				s += " "
			s += " | "
		s += "\n  " + dottedLine
		s += "\n  " + "  A   B   C   D   E   F   G   H\n"
		return s

	def movePiece(self, fromsq, tosq):
		# TODO validity checks, castling, promotion, enpassant
		# check if move is castle
		# TODO move all checks to pieces moveTo method, or we check this everytime
		castleMoves = [(58,60),(62,60),(2,4),(6,4)]
		for mov in range(4):
			if fromsq == castleMoves[mov][1]:
				if tosq == castleMoves[mov][0]:
					try: 
						self.castle(mov)
					except(IllegalMoveException):
						print("Illegal move.")
					else:
						return True
				elif isinstance(self.board[fromsq], King):
					# king is moved but not castled, reduce castling rights
					if self.board[fromsq].color == Color.WHITE:
						self.castlingRights[0] = False
						self.castlingRights[1] = False
					else:
						self.castlingRights[2] = False
						self.castlingRights[3] = False
		# check if rook moved to reduce castling rights
		rookinits = [56, 63, 0, 15]
		if fromsq in rookinits and isinstance(self.board[fromsq], Rook):
			self.castlingRights[rookinits.index(fromsq)] = False
		try:
			self.board[fromsq].moveTo(tosq, self)
		except IllegalMoveException:
			print("Illegal move.")
			return False
		else:
			self.board[tosq] = self.board[fromsq]
			self.board[fromsq] = None
			return True

	def castle(self, cIndex):
		# cIndex: white queenside, white kingside, black queenside, black kingside
		if not(self.castlingRights[cIndex]):
			raise IllegalMoveException
		# fields that need to be free:
		free = [range(57,60), [61, 62], range(1,4), [5,6]]
		for i in free[cIndex]:
			if self.board[i]:
				raise IllegalMoveException
		moves = [(58,60,59,56),(62,60,61,63),(2,4,3,0),(6,4,5,7)]
		# fields are free and we have castling rights
		# good players always move the king first
		self.board[moves[cIndex][0]] = self.board[moves[cIndex][1]]
		self.board[moves[cIndex][1]] = None
		self.board[moves[cIndex][0]].position = moves[cIndex][0]
		self.board[moves[cIndex][0]].updateValue()
		# then the rook
		self.board[moves[cIndex][2]] = self.board[moves[cIndex][3]]
		self.board[moves[cIndex][3]] = None
		self.board[moves[cIndex][2]].position = moves[cIndex][0]
		self.board[moves[cIndex][0]].updateValue()
				
	def evaluate(self):
		black = 0
		white = 0
		for piece in self.board:
			if piece:
				if piece.color == Color.WHITE:
					white += piece.value
				elif piece.color == Color.BLACK:
					black += piece.value
		return (white,black)
	
	def undo(self):
		self = deepcopy(self.moveList[len(self.moveList)-2])

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
		self.value = self.tbl_king_end[pos] * (1 - current.gameIndex) + self.valuetbl[pos] * (current.gameIndex)

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

def print_help():
	print("In mbc you can use the following commands:")
	print("e - Evaluate Position")
	print("h - Help")
	print("n - New Game")
	print("q - Quit")
	print("u - Undo Move")
	print("Enter moves in Coordinate notation, e.g. g1f3")

def translate_notation(token):
	# TODO check validity
	fromstr, tostr = token[:2],token[2:]
	for i in range(len(notation)):
		if notation[i] == fromstr:
			fromint = i
		if notation[i] == tostr:
			toint = i
	return (fromint,toint)

# TODO make this recursive
def bestMove(pos, col):
	# copy initial position for restoration
	maximum = 0
	bestmove = None
	# iterate through squares
	for piece in pos.board:
		# if there is a piece and it's our color
		if piece and piece.color == col:
			possibleSquares = piece.attackSquares(pos)
			fromsq = piece.position
			# iterate through allsquares
			for tosq in possibleSquares:
				try:
					print("considering: ", type(piece), fromsq, tosq)
					pos.movePiece(fromsq, tosq)
				except IllegalMoveException:
					# if this happens, something is seriously wrong
					exit("ILLEGAL MOVE: ", type(piece), fromsq, tosq)
				else:
					# evaluate new position
					scoreTuple = pos.evaluate()
					if col == Color.WHITE:
						score = scoreTuple[0] - scoreTuple[1]
					else:
						score = scoreTuple[1] - scoreTuple[0]
					# if it scores better than max, make it new max
					print("position value: ", score)
					if score > maximum or bestmove == None:
						maximum = score
						bestmove = (fromsq, tosq)
					# restore initial position
					pos.board[fromsq] = piece
					pos.board[tosq] = None
					piece.position = fromsq
					piece.updateValue(pos)
	return bestmove

# MAIN ROUTINE
now = Position()
p = 0
token = ""
move = 0
colors = [Color.WHITE, Color.BLACK]
print("Welcome to mbc - Enter h for help.")
while (token != "q"):
	sideToMove = colors[move % 2]
	if now:
		print(now)
	token = input("mbc>")
	if token == "h":
		print_help()
	elif token == "n":
		now = Position()
	elif token == "e":
		score = now.evaluate()
		print("White:",score[0],"Black:",score[1])
	elif token == "t":
		best = bestMove(now,sideToMove)
		now.movePiece(best[0],best[1])
		move += 1
	elif len(token) == 4 or len(token) == 5:
		tup = translate_notation(token)
		now.movePiece(tup[0],tup[1])
		move += 1
	elif token == "q":
		break
	elif token == "u":
		now.undo()
	else:
		print("unknown command - enter h for help.")

