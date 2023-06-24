import pygame
from pygame.locals import *

from ChineseChessBoard import ChineseChessBoard


def deserialize(line):
    board = []
    for i in range(10):
        m = []
        for j in range(9):
            m.append(line[i * 9 + j])
        board.append(m)
    return board


class Debugger(object):
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("cchess")
        self.__screen = pygame.display.set_mode((720, 800), 0, 32)
        self.__background = pygame.image.load('../images/boardchess.jpg').convert()

        self.__chess_file_mapping = {('R', 'red_rook'), ('N', 'red_knight'), ('B', 'red_bison'), ('A', 'red_advisor'),
                                     ('C', 'red_cannon'), ('P', 'red_pawn'), ('K', 'red_king'),
                                     ('r', 'black_rook'), ('n', 'black_knight'), ('b', 'black_bison'),
                                     ('a', 'black_advisor'), ('c', 'black_cannon'), ('p', 'black_pawn'),
                                     ('k', 'black_king')}
        self.__chess_img_mapping = {}
        for (key, name) in self.__chess_file_mapping:
            self.__chess_img_mapping[key] = pygame.image.load('../images/' + name + '.jpg')

    def put_piece(self, piece, position):
        row, col = position
        self.__screen.blit(self.__chess_img_mapping[piece], (col * 80, row * 80))

    def refresh_board(self, board):
        self.__screen.blit(self.__background, (0, 0))
        piece_dict = board.get_all_piece_position()
        for piece in piece_dict:
            for pos in piece_dict[piece]:
                self.put_piece(piece, pos)
        pygame.display.update()

    def run(self):
        lines = []  # 存储每一行的列表

        with open("steps.txt", 'r') as file:
            for line in file.readlines():
                lines.append(line.rstrip('\n'))
        index = 0
        steps = []
        for line in lines:
            steps.append(deserialize(line))

        brd = ChineseChessBoard()
        brd.board = steps[0]
        self.refresh_board(brd)

        while True:
            for event in pygame.event.get():
                keys = pygame.key.get_pressed()
                if keys[K_DOWN] or keys[K_RIGHT]:
                    index += 1
                    if len(lines) > index >= 0:
                        brd.board = steps[index]
                        self.refresh_board(brd)

                if keys[K_UP] or keys[K_LEFT]:
                    index -= 1
                    if len(lines) > index >= 0:
                        brd.board = steps[index]
                        self.refresh_board(brd)

                if event.type == QUIT:
                    exit()


if __name__ == '__main__':
    e = Debugger()
    e.run()
