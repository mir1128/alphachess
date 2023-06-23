from GameInterface import GameInterface
import random


class ChineseChessBoard(GameInterface):
    def __init__(self):
        self.board = [
            ['r', 'n', 'b', 'a', 'k', 'a', 'b', 'n', 'r'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['_', 'c', '_', '_', '_', '_', '_', 'c', '_'],
            ['p', '_', 'p', '_', 'p', '_', 'p', '_', 'p'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['P', '_', 'P', '_', 'P', '_', 'P', '_', 'P'],
            ['_', 'C', '_', '_', '_', '_', '_', 'C', '_'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['R', 'N', 'B', 'A', 'K', 'A', 'B', 'N', 'R']
        ]
        self.is_red_turn = True
        self.is_game_over = False
        self.num_steps_no_capture = 0
        self.winner = None

    def encode(self):
        return "".join(["".join(row) for row in self.board])

    def get_all_piece_position(self):
        piece_positions = {}
        for i, row in enumerate(self.board):
            for j, piece in enumerate(row):
                if piece != '_':
                    if piece not in piece_positions:
                        piece_positions[piece] = []
                    piece_positions[piece].append((i, j))
        return piece_positions

    def generate_next_states(self):
        next_states = []
        for x in range(10):
            for y in range(9):
                piece = self.board[x][y]
                if piece != '_' and piece.islower() != self.is_red_turn:
                    piece_moves = self.get_piece_moves((x, y))
                    for move in piece_moves:
                        next_state = self.copy()
                        next_state.move_piece((x, y), move)
                        next_states.append((next_state, (x, y), move))
        return next_states

    def random_move(self):
        legal_moves = []
        for x in range(10):
            for y in range(9):
                piece = self.board[x][y]
                if piece != '_' and piece.islower() == self.is_red_turn:
                    piece_moves = self.get_piece_moves((x, y))
                    for move in piece_moves:
                        legal_moves.append(((x, y), move))
        if legal_moves:
            return random.choice(legal_moves)
        return None

    def get_final_reward(self):
        if self.is_draw():
            return 0
        if self.winner is not None:
            if self.winner == 'red':
                return 1
            else:
                return -1
        return None

    def copy(self):
        copied_board = ChineseChessBoard()
        copied_board.board = [row.copy() for row in self.board]
        copied_board.is_red_turn = self.is_red_turn
        copied_board.is_game_over = self.is_game_over
        copied_board.num_steps_no_capture = self.num_steps_no_capture
        copied_board.winner = self.winner
        return copied_board

    def game_over(self):
        if self.is_game_over:
            return True
        if self.is_draw():
            return True
        if self.is_checkmate():
            self.is_game_over = True
            self.winner = 'black' if self.is_red_turn else 'red'
            return True
        return False

    def move_piece(self, start_pos, end_pos):
        if not self.is_game_over:
            start_x, start_y = start_pos
            end_x, end_y = end_pos
            piece = self.board[start_x][start_y]
            target = self.board[end_x][end_y]

            if self.is_valid_move(start_pos, end_pos):
                self.board[end_x][end_y] = piece
                self.board[start_x][start_y] = '_'

                if target.lower() == 'k':
                    self.is_game_over = True

                    if target.islower():
                        self.winner = 'red'
                    else:
                        self.winner = 'black'

                self.is_red_turn = not self.is_red_turn

            if target != '_':
                self.num_steps_no_capture = 0
            else:
                self.num_steps_no_capture += 1

    def is_draw(self, max_steps_no_capture=60):
        return self.num_steps_no_capture >= max_steps_no_capture

    def is_valid_move(self, start_pos, end_pos):
        start_x, start_y = start_pos
        piece = self.board[start_x][start_y]

        # 如果起始位置没有棋子，返回False
        if piece == '_':
            return False

        # 确保棋子的颜色与当前回合颜色相符
        if self.is_red_turn and piece.islower():
            return False
        if not self.is_red_turn and piece.isupper():
            return False

        # 获取给定棋子的所有合法走子
        legal_moves = self.get_piece_moves(start_pos)

        # 检查终止位置是否在合法走子中
        return end_pos in legal_moves

    def get_piece_moves(self, position):
        x, y = position
        piece = self.board[x][y]

        piece_type = piece.lower()
        moves = []

        if piece_type == 'k':
            moves = self.get_piece_king_moves(position)
        elif piece_type == 'a':
            moves = self.get_piece_advisor_moves(position)
        elif piece_type == 'b':
            moves = self.get_piece_bison_moves(position)
        elif piece_type == 'n':
            moves = self.get_piece_knight_moves(position)
        elif piece_type == 'r':
            moves = self.get_piece_rook_moves(position)
        elif piece_type == 'c':
            moves = self.get_piece_canon_moves(position)
        elif piece_type == 'p':
            moves = self.get_piece_pawn_moves(position)

        return moves

    def get_piece_king_moves(self, position):
        x, y = position
        piece = self.board[x][y]
        moves = []

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if 0 <= nx < 10 and 0 <= ny < 9:
                # 帅/将的宫限制
                if piece.islower() and (0 <= nx <= 2) and (3 <= ny <= 5):
                    target = self.board[nx][ny]
                    if target == '_' or target.isupper():
                        moves.append((nx, ny))
                elif piece.isupper() and (7 <= nx <= 9) and (3 <= ny <= 5):
                    target = self.board[nx][ny]
                    if target == '_' or target.islower():
                        moves.append((nx, ny))

                if piece == 'K' and nx == x - 1 and ny == y:
                    # 判断将/帅之间是否隔着棋子
                    for i in range(x - 1, -1, -1):
                        if self.board[i][y] != '_' and self.board[i][y] != 'k':
                            break
                        if self.board[i][y] == 'k':
                            moves.append((i, y))
                            break

                elif piece == 'k' and nx == x + 1 and ny == y:
                    for i in range(x + 1, 10):
                        if self.board[i][y] != '_' and self.board[i][y] != 'K':
                            break
                        if self.board[i][y] == 'K':
                            moves.append((i, y))

        return moves

    def get_piece_advisor_moves(self, position):
        x, y = position
        piece = self.board[x][y]
        moves = []

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if 0 <= nx < 10 and 0 <= ny < 9:
                # 士/仕的宫限制
                if piece.islower() and (3 <= ny <= 5) and (0 <= nx <= 2):
                    target = self.board[nx][ny]
                    if target == '_' or target.isupper():
                        moves.append((nx, ny))
                elif piece.isupper() and (3 <= ny <= 5) and (7 <= nx <= 9):
                    target = self.board[nx][ny]
                    if target == '_' or target.islower():
                        moves.append((nx, ny))

        return moves

    def get_piece_bison_moves(self, position):
        x, y = position
        piece = self.board[x][y]
        moves = []

        directions = [(-2, -2), (-2, 2), (2, -2), (2, 2)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            # 确保在棋盘内
            if 0 <= nx < 10 and 0 <= ny < 9:
                target = self.board[nx][ny]
                # 没有越过河
                if piece.islower() and (0 <= nx <= 4) or piece.isupper() and (5 <= nx <= 9):
                    # 没有被蹩腿
                    blocking_x, blocking_y = (x + dx // 2, y + dy // 2)
                    blocking_piece = self.board[blocking_x][blocking_y]
                    if blocking_piece == '_':
                        if target == '_' or piece.islower() != target.islower():
                            moves.append((nx, ny))

        return moves

    def get_piece_rook_moves(self, position):
        x, y = position
        piece = self.board[x][y]
        moves = []

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            while 0 <= nx < 10 and 0 <= ny < 9:
                target = self.board[nx][ny]
                if target == '_':
                    moves.append((nx, ny))
                else:
                    if piece.islower() != target.islower():
                        moves.append((nx, ny))
                    break

                nx, ny = nx + dx, ny + dy

        return moves

    def get_piece_knight_moves(self, position):
        x, y = position
        piece = self.board[x][y]
        moves = []

        offsets = [
            (-1, -2), (1, -2), (-1, 2), (1, 2),
            (-2, -1), (-2, 1), (2, -1), (2, 1)
        ]

        for dx, dy in offsets:
            nx, ny = x + dx, y + dy

            # 确保在棋盘内
            if 0 <= nx < 10 and 0 <= ny < 9:
                target = self.board[nx][ny]
                # 没有被蹩腿
                blocking_x, blocking_y = x, y
                if dx == 2 or dx == -2:
                    blocking_x = x + dx // 2
                elif dy == 2 or dy == -2:
                    blocking_y = y + dy // 2
                blocking_piece = self.board[blocking_x][blocking_y]
                if blocking_piece == '_':
                    if target == '_' or piece.islower() != target.islower():
                        moves.append((nx, ny))

        return moves

    def get_piece_canon_moves(self, position):
        x, y = position
        piece = self.board[x][y]
        moves = []

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            has_cannon = False

            while 0 <= nx < 10 and 0 <= ny < 9:
                target = self.board[nx][ny]

                if not has_cannon:
                    if target == '_':
                        moves.append((nx, ny))
                    else:
                        has_cannon = True
                else:
                    if target != '_':
                        if piece.islower() != target.islower():
                            moves.append((nx, ny))
                        break

                nx, ny = nx + dx, ny + dy

        return moves

    def get_piece_pawn_moves(self, position):
        x, y = position
        piece = self.board[x][y]
        moves = []

        if piece.islower():
            directions = [(1, 0)]
            if x >= 5:
                directions.extend([(0, 1), (0, -1)])
        else:
            directions = [(-1, 0)]
            if x <= 4:
                directions.extend([(0, 1), (0, -1)])

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if 0 <= nx < 10 and 0 <= ny < 9:
                target = self.board[nx][ny]
                if target == '_' or piece.islower() != target.islower():
                    moves.append((nx, ny))

        return moves

    def is_in_check(self, is_red_turn):
        king_symbol = 'K' if is_red_turn else 'k'
        king_position = None

        # 寻找当前玩家的帅/将的位置
        for x in range(10):
            for y in range(9):
                if self.board[x][y] == king_symbol:
                    king_position = (x, y)
                    break
            if king_position is not None:
                break

        # 遍历棋盘上所有对方棋子的可移动位置，判断是否将军
        for x in range(10):
            for y in range(9):
                piece = self.board[x][y]
                if piece != '_' and piece.islower() != king_symbol.islower():
                    piece_moves = self.get_piece_moves((x, y))
                    if king_position in piece_moves:
                        return True

        return False

    def is_checkmate(self):
        is_red_turn = self.is_red_turn

        if not self.is_in_check(is_red_turn):
            return False

        for x in range(10):
            for y in range(9):
                piece = self.board[x][y]
                if piece != '_' and piece.islower() == is_red_turn:
                    piece_moves = self.get_piece_moves((x, y))

                    for move in piece_moves:
                        # 尝试走子
                        origin_piece = self.board[move[0]][move[1]]
                        self.board[move[0]][move[1]] = piece
                        self.board[x][y] = '_'

                        # 检查是否摆脱了将军状态
                        is_safe = not self.is_in_check(is_red_turn)

                        # 撤销走子
                        self.board[x][y] = piece
                        self.board[move[0]][move[1]] = origin_piece

                        if is_safe:
                            return False

        return True

    def print_board(self):
        board_symbols = {
            'k': '将', 'K': '帅',
            'a': '士', 'A': '仕',
            'b': '象', 'B': '相',
            'n': '马', 'N': '马',
            'r': '车', 'R': '車',
            'c': '炮', 'C': '砲',
            'p': '卒', 'P': '兵',
            '_': '十'
        }

        print("  0 1 2 3 4 5 6 7 8")
        for x in range(10):
            row = []
            for y in range(9):
                piece = self.board[x][y]
                row.append(board_symbols[piece])
            print(f"{x} {' '.join(row)}")

    def show_result(self):
        if self.is_draw():
            print("游戏结束，和棋！")
        elif self.winner is not None:
            print(f"游戏结束，胜利者是 {self.winner}！")
        else:
            print("游戏未结束")


def test_king_moves():
    # 创建一个棋盘实例
    chess_board = ChineseChessBoard()

    # 测试get_piece_king_moves
    chess_board.board = [
        ['_', '_', '_', '_', '_', '_', '_', '_', '_'] for _ in range(10)
    ]

    # 红帅和黑将的位置
    chess_board.board[9][4] = 'K'
    chess_board.board[8][4] = '_'
    chess_board.board[0][4] = 'k'

    king_test_cases = [
        ((9, 4), [('K', [(0, 4), (8, 4), (9, 3), (9, 5)])]),
        ((0, 4), [('k', [(1, 4), (0, 3), (0, 5), (9, 4)])])
    ]

    chess_board.print_board()

    for position, expected in king_test_cases:
        actual = chess_board.get_piece_king_moves(position)
        actual_sorted = sorted(actual, key=lambda x: (x[0], x[1]))
        expected_sorted = sorted(expected[0][1], key=lambda x: (x[0], x[1]))
        assert actual_sorted == expected_sorted


def test_advisor_moves():
    # 创建一个棋盘实例
    chess_board = ChineseChessBoard()

    # 测试get_piece_advisor_moves
    chess_board.board = [
        ['_', '_', '_', '_', '_', '_', '_', '_', '_'] for _ in range(10)
    ]
    chess_board.board[0][3] = 'a'
    chess_board.board[0][5] = 'a'
    chess_board.board[9][3] = 'A'
    chess_board.board[9][5] = 'A'

    advisor_test_cases = [
        ((0, 3), [('a', [(1, 4)])]),
        ((0, 5), [('a', [(1, 4)])]),
        ((9, 3), [('A', [(8, 4)])]),
        ((9, 5), [('A', [(8, 4)])])
    ]

    for position, expected in advisor_test_cases:
        actual = chess_board.get_piece_advisor_moves(position)
        expected_sorted = sorted(expected[0][1], key=lambda x: (x[0], x[1]))
        assert actual == expected_sorted


def test_bison_moves():
    chess_board = ChineseChessBoard()
    # 测试get_piece_bison_moves
    chess_board.board[0][2] = 'b'
    chess_board.board[0][6] = 'b'
    chess_board.board[9][2] = 'B'
    chess_board.board[9][6] = 'B'

    bison_test_cases = [
        ((0, 2), [('b', [(2, 0), (2, 4)])]),
        ((0, 6), [('b', [(2, 4), (2, 8)])]),
        ((9, 2), [('B', [(7, 0), (7, 4)])]),
        ((9, 6), [('B', [(7, 4), (7, 8)])])
    ]

    for position, expected in bison_test_cases:
        actual = chess_board.get_piece_bison_moves(position)
        expected_sorted = sorted(expected[0][1], key=lambda x: (x[0], x[1]))
        assert actual == expected_sorted


def test_rook_moves():
    chess_board = ChineseChessBoard()
    # 测试get_piece_rook_moves
    chess_board.board[0][0] = 'r'
    chess_board.board[0][8] = 'r'
    chess_board.board[9][0] = 'R'
    chess_board.board[9][8] = 'R'

    rook_test_cases = [
        ((0, 0), [('r', [(1, 0), (2, 0)])]),
        ((0, 8), [('r', [(1, 8), (2, 8)])]),
        ((9, 0), [('R', [(8, 0), (7, 0)])]),
        ((9, 8), [('R', [(7, 8), (8, 8)])])
    ]

    for position, expected in rook_test_cases:
        actual = chess_board.get_piece_rook_moves(position)
        actual_sorted = sorted(actual, key=lambda x: (x[0], x[1]))
        expected_sorted = sorted(expected[0][1], key=lambda x: (x[0], x[1]))
        assert actual_sorted == expected_sorted


def test_knight_moves():
    chess_board = ChineseChessBoard()
    # 测试get_piece_knight_moves
    chess_board.board[9][1] = 'N'
    chess_board.board[9][7] = 'N'
    chess_board.board[0][1] = 'n'
    chess_board.board[0][7] = 'n'

    knight_test_cases = [
        ((0, 1), [('n', [(2, 0), (2, 2)])]),
        ((0, 7), [('n', [(2, 6), (2, 8)])]),
        ((9, 1), [('N', [(7, 0), (7, 2)])]),
        ((9, 7), [('N', [(7, 6), (7, 8)])])
    ]

    for position, expected in knight_test_cases:
        actual = chess_board.get_piece_knight_moves(position)
        actual_sorted = sorted(actual, key=lambda x: (x[0], x[1]))
        expected_sorted = sorted(expected[0][1], key=lambda x: (x[0], x[1]))
        assert actual_sorted == expected_sorted


def test_canon_moves():
    chess_board = ChineseChessBoard()
    # 测试get_piece_canon_moves
    chess_board.board[2][1] = 'c'
    chess_board.board[2][7] = 'c'
    chess_board.board[7][1] = 'C'
    chess_board.board[7][7] = 'C'

    canon_test_cases = [
        ((2, 1),
         [('c', [(1, 1), (2, 0), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (3, 1), (4, 1), (5, 1), (6, 1), (9, 1)])]),
        ((2, 7),
         [('c', [(2, 8), (3, 7), (4, 7), (5, 7), (6, 7), (9, 7), (2, 6), (2, 5), (2, 4), (2, 3), (2, 2), (1, 7)])]),
        ((7, 1),
         [('C', [(7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (8, 1), (7, 0), (6, 1), (5, 1), (4, 1), (3, 1), (0, 1)])]),
        ((7, 7),
         [('C', [(7, 8), (8, 7), (7, 6), (7, 5), (7, 4), (7, 3), (7, 2), (6, 7), (5, 7), (4, 7), (3, 7), (0, 7)])])
    ]

    for position, expected in canon_test_cases:
        actual = chess_board.get_piece_canon_moves(position)
        actual_sorted = sorted(actual, key=lambda x: (x[0], x[1]))
        expected_sorted = sorted(expected[0][1], key=lambda x: (x[0], x[1]))
        assert actual_sorted == expected_sorted


def test_pawn_moves():
    chess_board = ChineseChessBoard()
    # 测试get_piece_pawn_moves
    chess_board.board[3][0] = 'p'
    chess_board.board[3][2] = 'p'
    chess_board.board[3][4] = 'p'
    chess_board.board[3][6] = 'p'
    chess_board.board[3][8] = 'p'
    chess_board.board[6][0] = 'P'
    chess_board.board[6][2] = 'P'
    chess_board.board[6][4] = 'P'
    chess_board.board[6][6] = 'P'
    chess_board.board[6][8] = 'P'

    pawn_test_cases = [
        ((3, 0), [('p', [(4, 0)])]),
        ((3, 2), [('p', [(4, 2)])]),
        ((3, 4), [('p', [(4, 4)])]),
        ((3, 6), [('p', [(4, 6)])]),
        ((3, 8), [('p', [(4, 8)])]),
        ((6, 0), [('P', [(5, 0)])]),
        ((6, 2), [('P', [(5, 2)])]),
        ((6, 4), [('P', [(5, 4)])]),
        ((6, 6), [('P', [(5, 6)])]),
        ((6, 8), [('P', [(5, 8)])])
    ]

    for position, expected in pawn_test_cases:
        actual = chess_board.get_piece_pawn_moves(position)
        actual_sorted = sorted(actual, key=lambda x: (x[0], x[1]))
        expected_sorted = sorted(expected[0][1], key=lambda x: (x[0], x[1]))
        assert actual_sorted == expected_sorted


def red_win():
    # 红方胜利的棋谱
    red_wins_moves = [
        ((6, 4), (5, 4)),  # 红兵向前
        ((3, 4), (4, 4)),  # 黑兵向前
        ((5, 4), (4, 4)),  # 红兵横向移动
        ((3, 2), (4, 2)),  # 黑兵向前
        ((7, 1), (7, 4)),  # 红炮当头
        ((4, 2), (5, 2)),  # 黑兵向前
        ((7, 4), (0, 4))  # 红帅炮掉黑将，红方胜利
    ]

    # 初始化棋盘
    chess_board = ChineseChessBoard()

    # 按照棋谱执行走子操作
    for move in red_wins_moves:
        start, end = move
        chess_board.move_piece(start, end)

    chess_board.print_board()
    # 检查游戏是否结束，红方是否胜利
    assert chess_board.is_game_over
    assert chess_board.winner == 'red'


def draw():
    # 初始化棋盘
    chess_board = ChineseChessBoard()
    chess_board.board = \
        [
            ['r', 'n', 'b', 'a', 'k', 'a', 'b', 'n', 'r'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['_', 'c', '_', '_', '_', '_', '_', 'c', '_'],
            ['P', '_', 'p', '_', 'p', '_', 'p', '_', '-'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['_', '_', 'P', '_', 'P', '_', 'P', '_', 'p'],
            ['_', 'C', '_', '_', '_', '_', '_', 'C', '_'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['R', 'N', 'B', 'A', 'K', 'A', 'B', 'N', 'R']
        ]

    # 和棋的棋谱
    draw_moves = [
                     ((3, 0), (3, 1)),  # 红兵向前
                     ((6, 8), (6, 7)),  # 红兵向后
                     ((3, 1), (3, 0)),  # 黑兵向前
                     ((6, 7), (6, 8)),  # 黑兵向后
                 ] * 15  # 持续30步无子落地，共计60步

    # 按照棋谱执行走子操作
    for move in draw_moves:
        start, end = move
        chess_board.move_piece(start, end)

    # 检查游戏是否和棋
    assert chess_board.is_draw()


def test_red_win_king_eat_king():
    # 红方胜利的棋谱
    red_wins_moves = [
        ((6, 4), (5, 4)),  # 红兵向前
        ((3, 4), (4, 4)),  # 黑兵向前
        ((5, 4), (4, 4)),  # 红兵吃掉黑兵
        ((3, 2), (4, 2)),  # 黑兵向前
        ((4, 4), (4, 3)),  # 红炮横向移动
        ((0, 4), (9, 4))  # 黑将吃掉红帅
    ]

    # 初始化棋盘
    chess_board = ChineseChessBoard()

    # 按照棋谱执行走子操作
    for move in red_wins_moves:
        start, end = move
        chess_board.move_piece(start, end)
        chess_board.print_board()

    # 检查游戏是否结束，红方是否胜利
    assert chess_board.is_game_over
    assert chess_board.winner == 'black'


def test_get_all_piece_position():
    chess_board = ChineseChessBoard()
    pos = chess_board.get_all_piece_position()

    a = 0;


if __name__ == '__main__':
    test_king_moves()
    test_advisor_moves()
    test_bison_moves()
    test_rook_moves()
    test_knight_moves()
    test_canon_moves()
    test_pawn_moves()
    red_win()
    draw()
    test_red_win_king_eat_king()
    test_get_all_piece_position()

    board = ChineseChessBoard()
    print(board.encode())

