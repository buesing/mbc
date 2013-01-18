#/usr/bin/env python

from defs import *
from position import Position

def print_help():
	print("In mbc you can use the following commands:")
	print("e - Evaluate Position")
	print("h - Help")
	print("n - New Game")
	print("q - Quit")
	print("u - Undo Move")
	print("t - Think and make best move")
	print("f - Print FEN String")
	print("p <FEN STRING> - Parse FEN String")
	print("Enter moves in Coordinate notation, e.g. g1f3")

def main():
	now = Position()
	p = 0
	token = ""
	move = 0
	sideToMove = Color.WHITE
	print("Welcome to mbc - Enter h for help.")
	while (token != "q"):
		sideToMove = 1 - sideToMove
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
			best = bestMove(now,sideToMove, None, 2)
			print(best)
			try:
				now.movePiece(best[0],best[1])
			except IllegalMoveException:
				print("bestMove has returned Illegal Move")
			else:
				move += 1
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
			except:
				print("Illegal Move")
			else:
				if now.board[tup[0]].color != sideToMove:
					print("Illegal Move")
				else:
					try:
						now.movePiece(tup[0],tup[1])
					except IllegalMoveException:
						print("Illegal Move")
					else:
						move += 1

if __name__ == "__main__":
	main()
