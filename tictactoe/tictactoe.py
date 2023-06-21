from copy import deepcopy


class Board:
    def __init__(self):
        # define players
        self.player_1 = 'x'
        self.player_2 = 'o'
        self.empty_square = '.'

        # define board position
        self.position = {}

        # init (reset) board
        self.init_board()

        # create a copy of a previous board state if available
        if board is not None:
            self.__dict__ = deepcopy(board.__dict__)

    def init_board(self):
        # loop over board rows
        for row in range(3):
            # loop over board columns
            for col in range(3):
                # set every board square to empty square
                self.position[row, col] = self.empty_square

    def make_move(self):
        # create new board instance that inherits from the current state
        board = Board(self)

        # make move
        board.position[row, col] = self.player_1

        # swap players
        (board.player_1, board.player_2) = (board.player_2, board.player_1)

        # return new board state
        return board

    def is_draw(self):
        # loop over board squares
        for row, col in self.position:
            # empty square is available
            if self.position[row, col] == self.empty_square:
                # this is not a draw
                return False

        # by default we return a draw
        return True

    def is_win(self):
        ##################################
        # vertical sequence detection
        ##################################

        # loop over board columns
        for col in range(3):
            # define winning sequence list
            winning_sequence = []

            # loop over board rows
            for row in range(3):
                # if found same next element in the row
                if self.position[row, col] == self.player_2:
                    # update winning sequence
                    winning_sequence.append((row, col))

                # if we have 3 elements in the row
                if len(winning_sequence) == 3:
                    # return the game is won state
                    return True

        ##################################
        # horizontal sequence detection
        ##################################

        # loop over board columns
        for row in range(3):
            # define winning sequence list
            winning_sequence = []

            # loop over board rows
            for col in range(3):
                # if found same next element in the row
                if self.position[row, col] == self.player_2:
                    # update winning sequence
                    winning_sequence.append((row, col))

                # if we have 3 elements in the row
                if len(winning_sequence) == 3:
                    # return the game is won state
                    return True

        ##################################
        # 1st diagonal sequence detection
        ##################################

        # define winning sequence list
        winning_sequence = []

        # loop over board rows
        for row in range(3):
            # init column
            col = row

            # if found same next element in the row
            if self.position[row, col] == self.player_2:
                # update winning sequence
                winning_sequence.append((row, col))

            # if we have 3 elements in the row
            if len(winning_sequence) == 3:
                # return the game is won state
                return True

        ##################################
        # 2nd diagonal sequence detection
        ##################################

        # define winning sequence list
        winning_sequence = []

        # loop over board rows
        for row in range(3):
            # init column
            col = 3 - row - 1

            # if found same next element in the row
            if self.position[row, col] == self.player_2:
                # update winning sequence
                winning_sequence.append((row, col))

            # if we have 3 elements in the row
            if len(winning_sequence) == 3:
                # return the game is won state
                return True

        # by default return non winning state
        return False

    def generate_states(self):
        # define states list (move list - list of available actions to consider)
        actions = []

        # loop over board rows
        for row in range(3):
            # loop over board columns
            for col in range(3):
                # make sure that current square is empty
                if self.position[row, col] == self.empty_square:
                    # append available action/board state to action list
                    actions.append(self.make_move(row, col))

        # return the list of available actions (board class instances)
        return actions

    def game_loop(self):
        print('\n  Tic Tac Toe by Code Monkey King\n')
        print('  Type "exit" to quit the game')
        print('  Move format [x,y]: 1,2 where 1 is column and 2 is row')

        # print board
        print(self)

        # create MCTS instance
        mcts = MCTS()

        # game loop
        while True:
            # get user input
            user_input = input('> ')

            # escape condition
            if user_input == 'exit': break

            # skip empty input
            if user_input == '': continue

            try:
                # parse user input (move format [col, row]: 1,2)
                row = int(user_input.split(',')[1]) - 1
                col = int(user_input.split(',')[0]) - 1

                # check move legality
                if self.position[row, col] != self.empty_square:
                    print(' Illegal move!')
                    continue

                # make move on board
                self = self.make_move(row, col)

                # print board
                print(self)

                # search for the best move
                best_move = mcts.search(self)

                # legal moves available
                try:
                    # make AI move here
                    self = best_move.board

                # game over
                except:
                    pass

                # print board
                print(self)

                # check if the game is won
                if self.is_win():
                    print('player "%s" has won the game!\n' % self.player_2)
                    break

                # check if the game is drawn
                elif self.is_draw():
                    print('Game is drawn!\n')
                    break

            except Exception as e:
                print('  Error:', e)
                print('  Illegal command!')
                print('  Move format [x,y]: 1,2 where 1 is column and 2 is row')


if __name__ == '__main__':
    # create board instance
    board = Board()

    # start game loop
    board.game_loop()