from copy import deepcopy

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
piece_str = "PNBRQK"
# lookup initial piece values
piece_values = [100, 325, 325, 500, 975, 20000]

class Color(object):
	WHITE = 0
	BLACK = 1

class IllegalMoveException(Exception):
	pass

class InvalidFENException(Exception):
	pass

def translate_notation(token):
	le = len(token)
	if le != 4 or le != 6:
		raise IllegalMoveException
	if not(token[:2] in notation):
		raise IllegalMoveException
	if not(token[2:4] in notation):
		raise IllegalMoveException
	if le == 6:
		if le[4] != "=":
			raise IllegalMoveException
		if not(le[5] in "NBRQnbrq"):
			raise IllegalMoveException
		# TODO promotion
	return notation.index(token[:2]),notation.index(token[2:])

# TODO make this recursive
def bestMove(position, bestmove, depth):
	if depth == 0:
		return position.evaluate()
	maximum = -99999999
	# iterate through squares
	for i in range(len(position.board)):
		# if there is a piece and it's our color
		if position.board[i] and position.board[i].color == color:
			possibleSquares = position.board[i].attackSquares(position)
			fromsq = position.board[i].position
			# iterate through allsquares
			for tosq in possibleSquares:
				print(depth, type(position.board[i]), tosq)
				try:
					position.movePiece(fromsq,tosq)
				except IllegalMoveException:
					print("Illegal move in bestMove()")
				else:
					score = -bestMove(depth - 1)
					# TODO undo move here!!
					# if it scores better than max, make it new max
					if score > maximum:
						maximum = score
					# restore initial position
	return maximum
