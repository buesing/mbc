from pieces import *
from defs import *
from string import digits

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
		self.fenList = []

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

	def movePiece(self, fromsq, tosq, promotion = None):
		if promotion is not None:
			if promotion == "Q":
				self.board[tosq] = Queen(tosq, self.sideToMove)
			elif promotion == "R":
				self.board[tosq] = Rook(tosq, self.sideToMove)
			elif promotion == "B":
				self.board[tosq] = Bishop(tosq, self.sideToMove)
			elif promotion == "N":
				self.board[tosq] = Knight(tosq, self.sideToMove)
			self.board[tosq].updateValue(self)
			self.board[fromsq] = None
			self.afterMoveRoutine(tosq, True)
			return
		self.fenList.append(self.makeFen())
		# TODO validity checks, promotion, enpassant
		if not(self.board[fromsq]):
			self.fenList = self.fenList[:len(self.fenList) - 1]
			raise IllegalMoveException
			return
		# TODO move all checks to pieces moveTo method, or we check this everytime
		if isinstance(self.board[fromsq], King):
			# TODO this is a little redundant. everytime the king is moved we reset castling rights
			castleMoves = [(58,60),(62,60),(2,4),(6,4)]
			# check if move is castle
			for mov in range(4):
				if fromsq == castleMoves[mov][1] and tosq == castleMoves[mov][0]:
					try:
						self.castle(mov)
					except IllegalMoveException:
						self.fenList = self.fenList[:len(self.fenList) - 1]
						raise
						return
					else:
						self.afterMoveRoutine(tosq, True)
						return
		# check if rook moved to reduce castling rights
		rookinits = [56, 63, 0, 15]
		if fromsq in rookinits and isinstance(self.board[fromsq], Rook):
			self.castlingRights[rookinits.index(fromsq)] = False
		if self.board[fromsq].moveTo(tosq, self):
			self.board[tosq] = self.board[fromsq]
			self.board[fromsq] = None
			self.afterMoveRoutine(tosq, (int(self.board[tosq]) == 0 or self.board[tosq]))
			return 
		else:
			self.fenList = self.fenList[:len(self.fenList) - 1]
			raise IllegalMoveException
			return
	
	def afterMoveRoutine(self,updateSq, resetPlies):
		# check if king is in check
		for piece in self.board:
			if isinstance(piece, King) and piece.color == self.sideToMove:
				if piece.inCheck(piece.position, self):
					self.fenList = self.fenList[:len(self.fenList) - 1]
					raise IllegalMoveException("King is put in check")
					return
		if self.sideToMove == Color.BLACK:
			self.moveNumber += 1
		if resetPlies:
			self.plies = 0
		else:
			self.plies += 1
		self.currentEval = self.evaluate()
		self.sideToMove = 1 - self.sideToMove

	def castle(self, cIndex):
		print(cIndex)
		# cIndex: white queenside, white kingside, black queenside, black kingside
		print(self.castlingRights[cIndex])
		if not(self.castlingRights[cIndex]):
			raise IllegalMoveException("No castling rights")
			return
		# fields that need to be free:
		free = [range(57,60), [61, 62], range(1,4), [5,6]]
		for i in free[cIndex]:
			if self.board[i]:
				raise IllegalMoveException("No castling rights")
				return
		moves = [(58,60,59,56),(62,60,61,63),(2,4,3,0),(6,4,5,7)]
		# fields are free and we have castling rights
		# pros always move the king first
		self.board[moves[cIndex][0]] = self.board[moves[cIndex][1]]
		self.board[moves[cIndex][1]] = None
		self.board[moves[cIndex][0]].position = moves[cIndex][0]
		self.board[moves[cIndex][0]].updateValue(self)
		# then the rook
		self.board[moves[cIndex][2]] = self.board[moves[cIndex][3]]
		self.board[moves[cIndex][3]] = None
		self.board[moves[cIndex][2]].position = moves[cIndex][0]
		self.board[moves[cIndex][0]].updateValue(self)
		# reduce castling rights
		if self.board[moves[cIndex][0]].color == Color.WHITE:
			self.castlingRights[0] = False
			self.castlingRights[1] = False
		else:
			self.castlingRights[2] = False
			self.castlingRights[3] = False
		return
				
	def promote(self, fromsq, tosq, prom):
		try:
			self.movePiece(fromsq, tosq)
		except IllegalMoveException:
			print("Illegal Move")
		char = prom.upper()
		if char == "N":
			board[tosq] = Knight(tosq,self.sideToMove)
		elif char == "B":
			board[tosq] = Bishop(tosq,self.sideToMove)
		elif char == "R":
			board[tosq] = Rook(tosq,self.sideToMove)
		elif char == "Q":
			board[tosq] = Queen(tosq,self.sideToMove)
		
	def evaluate(self):
		black = 0
		white = 0
		for p in self.board:
			if p:
				if p.color == Color.WHITE:
					white += p.value
				elif p.color == Color.BLACK:
					black += p.value
		if self.sideToMove == Color.WHITE:
			return white - black
		else:
			return black - white
	
	def undo(self):
		if len(self.fenList):
			self.parseFen(self.fenList[len(self.fenList)-1])
			self.fenList = self.fenList[:len(self.fenList)-1]
		else:
			print("No move to undo.")
	
	def makeFen(self):
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
					empty = 0
				fen += str(self.board[i])
		fen += " "
		if self.sideToMove == Color.WHITE:
			fen += "w"
		else:
			fen += "b"
		fen += " "
		if sum(self.castlingRights) == 0:
			fen += "-"
		else:
			cast = [self.castlingRights[1],self.castlingRights[0],self.castlingRights[3],self.castlingRights[2]]
			fencast = "KQkq"
			for i in range(len(cast)):
				if cast[i]:
					fen += fencast[i]
		fen += " "
		if self.epSquare != -1:
			fen += notation[self.epSquare]
		else:
			fen += "-"
		fen += " "
		fen += str(self.plies)
		fen += " "
		fen += str(self.moveNumber)
		return fen
	
	def parseFen(self, afen):
		fen = afen.split(" ")
		if len(fen) != 6:
			raise InvalidFENException("Length is not 6")
		brd = fen[0].replace("/", "")
		index = 0
		# board parsing
		for char in brd:
			if char in digits:
				for i in range(int(char)):
					self.board[index] = None
					index += 1
			else:
				if char.islower():
					color = Color.BLACK
					char = char.upper()
				else:
					color = Color.WHITE
				if char == "P":
					self.board[index] = Pawn(index,color)
				elif char == "N":
					self.board[index] = Knight(index,color)
				elif char == "B":
					self.board[index] = Bishop(index,color)
				elif char == "R":
					self.board[index] = Rook(index,color)
				elif char == "Q":
					self.board[index] = Queen(index,color)
				elif char == "K":
					self.board[index] = King(index,color)
				else:
					raise InvalidFENException("Unable to parse piece")
				index += 1
		# side to move
		if fen[1] == "w":
			self.sideToMove = Color.WHITE
		elif fen[1] == "b":
			self.sideToMove = Color.BLACK
		else:
			raise InvalidFENException("Side to move is invalid")
		# castling rights
		fencastle = "QKqk"
		if fen[2] == "-":
			self.castlingRights = [False for i in range(4)]
		for i in range(4):
			if fencastle[i] in fen[2]:
				self.castlingRights[i] = True
			else:
				self.castlingRights[i] = False
		# en passant square
		if fen[3] == "-":
			self.epSquare = -1
		elif fen[3] in notation:
			self.epSquare = notation.index(fen[3])
		else:
			raise InvalidFENException("En passant square is invalid")
		# plies + move number
		try:
			self.plies = int(fen[4])
			self.moveNumber = int(fen[5])
		except:
			raise InvalidFENException("Plies or move number is invalid")
