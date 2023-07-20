from ChineseChessBoard import ChineseChessBoard
from mcst import MCTS


class GameLogic:
    def __init__(self):
        self.chess_board = None

    def start(self):
        # 初始化ChineseChessBoard实例
        self.chess_board = ChineseChessBoard()

    def run(self):

        self.chess_board.print_board()
        # 循环执行，直到游戏结束
        while not self.game_over():
            # 接收玩家输入
            player_start_pos, player_end_pos = self.get_player_move()

            # 更新棋盘状态
            self.chess_board.move_piece(player_start_pos, player_end_pos)

            # 执行MCTS搜索找到最佳走法
            c = 1.0 if self.chess_board.is_red_turn() else 1.2
            board_state, ai_move_start_pos, ai_move_end_pos = MCTS((self.chess_board, None, None), c).search(30)

            # 更新棋盘状态
            self.chess_board.move_piece(ai_move_start_pos, ai_move_end_pos)

            self.chess_board.print_board()

            # 检查游戏是否结束
            if self.game_over():
                self.show_result()

    def game_over(self):
        # 检查游戏是否结束的逻辑
        return self.chess_board.game_over()

    def get_player_move(self):
        while True:
            move = input("请输入您的走子，格式如：(0, 1) to (2, 3): ")

            try:
                start_pos_str, end_pos_str = move.split(" to ")
                start_pos = tuple(map(int, start_pos_str.strip("( )").split(",")))
                end_pos = tuple(map(int, end_pos_str.strip("( )").split(",")))

                if self.chess_board.is_valid_move(start_pos, end_pos):
                    return start_pos, end_pos
                else:
                    print("不合法的走子，请重新输入！")
            except (ValueError, IndexError):
                print("输入格式错误，请按照要求的格式输入！")

    def show_result(self):
        # 展示游戏结果的逻辑
        return self.chess_board.show_result()


if __name__ == "__main__":
    game = GameLogic()
    game.start()
    game.run()
