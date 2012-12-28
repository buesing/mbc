from pieces import *
from defs import *

class Position(object):
	def __init__(self):
		# -1 == no en passant square
		self.epSquare = -1
		# white queenside, white kingside, black queenside, black kingside
		self.castlingRights = [True,True,True,True]
		self.moveList = []
		# index is 1 in endgame
		self.gameIndex = 0
		# plies since last pawn move or capture
		self.plies = 0
		# TODO update this every move
		self.sideToMove = Color.WHITE
		self.moveNumber = 0
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
		self.currentEval = self.evaluate()

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
						if self.sideToMove == Color.BLACK:
							self.moveNumber += 1
						self.plies = 0
						self.currentEval = self.evaluate()
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
			if self.board[fromsq].code != 0 and not(self.board[tosq]):
				self.plies += 1
			else:
				self.plies = 0
			if self.sideToMove == Color.BLACK:
				self.moveNumber += 1
			self.moveNumber += 1
			self.board[tosq] = self.board[fromsq]
			self.board[fromsq] = None
			self.currentEval = self.evaluate()
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
		for p in self.board:
			if p:
				if p.color == Color.WHITE:
					white += p.value
				elif p.color == Color.BLACK:
					black += p.value
		return (white,black)
	
	def undo(self):
		self = deepcopy(self.moveList[len(self.moveList)-2])
	
	def make_fen(self):
		empty = -1
		fen = ""
		for i in range(len(self.board)):
			if i % 8 == 0 and i != 0:
				if empty > 0:
					fen += str(empty)
					empty = 0
				fen += "/"
			if not(self.board[i]):
				if empty == -1:
					empty = 1
				else:
					empty += 1
			else:
				if empty > 0:
					fen += str(empty)
				fen += str(self.board[i])
		fen += " "
		if self.sideToMove == Color.WHITE:
			fen += "w"
		else:
			fen += "b"
		fen += " "
		cast = [self.castlingRights[1],self.castlingRights[0],self.castlingRights[3],self.castlingRights[2]]
		fencast = "KQkq"
		for i in range(len(cast)):
			if cast[i]:
				fen += fencast[i]
		if self.epSquare != -1:
			fen += notation[self.epSquare]
		fen += " "
		fen += str(self.plies)
		fen += " "
		fen += str(self.moveNumber)
		return fen
