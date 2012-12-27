#/usr/bin/env python

from defs import *
from pieces import *
from position import Position

def main():
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
			if now.board[tup[0]].color != sideToMove:
				print("Illegal Move")
			else:
				now.movePiece(tup[0],tup[1])
				move += 1
		elif token == "q":
			break
		elif token == "u":
			now.undo()

if __name__ == "__main__":
	main()
