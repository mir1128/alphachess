# -*- coding: utf-8 -*-

from sys import exit
from pygame.locals import *
from log.logger import logger
import pygame
from ChineseChessBoard import ChineseChessBoard
import tkinter as tk
from tkinter import messagebox


class GameUI(object):
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("cchess")
        self.__screen = pygame.display.set_mode((720, 800), 0, 32)
        self.__background = pygame.image.load('images/boardchess.jpg').convert()

        self.__chess_file_mapping = {('R', 'red_rook'), ('N', 'red_knight'), ('B', 'red_bison'), ('A', 'red_advisor'),
                                     ('C', 'red_cannon'), ('P', 'red_pawn'), ('K', 'red_king'),
                                     ('r', 'black_rook'), ('n', 'black_knight'), ('b', 'black_bison'),
                                     ('a', 'black_advisor'), ('c', 'black_cannon'), ('p', 'black_pawn'),
                                     ('k', 'black_king')}
        self.__chess_img_mapping = {}
        for (key, name) in self.__chess_file_mapping:
            self.__chess_img_mapping[key] = pygame.image.load('images/' + name + '.jpg')

    def put_piece(self, piece, position):
        row, col = position
        self.__screen.blit(self.__chess_img_mapping[piece], (col * 80, row * 80))

    def run(self):
        board = ChineseChessBoard()
        is_piece_picked = False
        piece_src_position = None

        while True:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    button_up_pos = pygame.mouse.get_pos()
                    if not is_piece_picked:
                        which_piece_is_picked = self.get_piece_by_position(board, button_up_pos)
                        if which_piece_is_picked != '_':
                            is_piece_picked = True
                            piece_src_position = button_up_pos
                            logger.info("pick an chess %s, src pos is %s", str(which_piece_is_picked), str(piece_src_position))
                    else:
                        src = self.to_board_pos(piece_src_position)
                        dst = self.to_board_pos(button_up_pos)
                        another_pick = self.get_piece_by_position(board, button_up_pos)

                        # pick another self chess
                        if another_pick != '_' and self.is_same_side(board, src, dst):
                            which_piece_is_picked = another_pick
                            piece_src_position = button_up_pos
                            logger.info("pick another chess %s, src pos is %s", str(which_piece_is_picked), str(piece_src_position))
                            break
                        else:
                            board.move_piece(src, dst)
                            is_piece_picked = False

                if event.type == QUIT:
                    exit()

                self.__screen.blit(self.__background, (0, 0))
                piece_dict = board.get_all_piece_position()
                for piece in piece_dict:
                    for pos in piece_dict[piece]:
                        self.put_piece(piece, pos)
                pygame.display.update()

                if board.is_game_over:
                    if board.is_draw():
                        show_message_box('游戏结束', '和棋')
                    if board.winner == 'red':
                        show_message_box('游戏结束', '红棋胜利')
                    else:
                        show_message_box('游戏结束', '黑棋胜利')
                    board = ChineseChessBoard()
                    continue

    def get_piece_by_position(self, board, button_up_pos):
        row, col = self.to_board_pos(button_up_pos)
        return board.board[row][col]

    def to_board_pos(self, pos):
        x, y = pos
        return int(y/80), int(x/80)

    def is_same_side(self, board, src, dst):
        src_row, src_col = src
        dst_row, dst_col = dst
        return board.board[src_row][src_col].islower() == board.board[dst_row][dst_col]


def show_message_box(title, message):
    root = tk.Tk()
    root.withdraw()  # 隐藏 tkinter 主窗口
    messagebox.showinfo(title, message)  # 显示消息框
    root.destroy()  # 销毁 tkinter 主窗口


if __name__ == '__main__':
    e = GameUI()
    e.run()
