#/usr/bin/env python

from defs import *
from position import Position

def print_help():
	print("\nIn mbc you can use the following commands:\n")
	print("h - Display this help menu")
	print("n - Start new game")
	print("q - Quit")
	print("e - Evaluate position")
	print("u - Undo Move")
	print("t - Think and make best move")
	print("f - Print FEN String")
	print("p <FEN STRING> - Parse FEN String\n")
	print("Enter moves in Coordinate notation, e.g. g1f3")
	print("For promotion append \"=?\" where ? is the acronym")
	print("for the piece you want to promote, e.g. c7c8=Q")
	print("For castling, just move the King to the appropriate square (no 0-0)")

def main():
	now = Position()
	token = ""
	print("Welcome to mbc - Enter h for help.")
	while (token != "q"):
		if now:
			print(now)
		token = input("mbc> ")
		if token == "h":
			print_help()
		elif token == "n":
			now = Position()
		elif token == "e":
			score = now.evaluate()
			print("White:",score[0],"Black:",score[1])
		elif token == "t":
			best = bestMove(now, 2)
			print(best)
			try:
				now.movePiece(best[0],best[1])
			except IllegalMoveException:
				print("bestMove has returned Illegal Move")
		elif token == "q":
			break
		elif token == "u":
			now.undo()
		elif token[0] == "p":
			now.parseFen(token[2:])
		elif token == "f":
			print(now.makeFen())
		else:
			try:
				tup = translate_notation(token)
			except TranslateException as e:
				print(e.msg)
			else:
				if now.board[tup[0]].color != now.sideToMove:
					print("Illegal Move: wrong side to move")
				else:
					if len(tup) == 3:
						try:
							now.movePiece(tup[0],tup[1],tup[2])
						except IllegalMoveException:
							print("Illegal Move: couldnt promote")
					else:
						try:
							now.movePiece(tup[0],tup[1])
						except IllegalMoveException:
							print("Illegal Move: couldnt move piece")
if __name__ == "__main__":
	main()
