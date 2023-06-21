import math
import random


class TreeNode():
    def __init__(self, board, parent):
        self.board = board

        # init is node terminal flag
        if self.board.is_win() or self.board.is_draw():
            # we have a terminal node
            self.is_terminal = True

        else:
            # we have a non-terminal node
            self.is_terminal = False

        # init is fully expanded flag
        self.is_fully_expanded = self.is_terminal

        # init parent node if available
        self.parent = parent

        # init the number of node visits
        self.visits = 0

        # init the total score of the node
        self.score = 0

        # init current node's children
        self.children = {}


class MCTS():
    def search(self, init_state):
        self.root = TreeNode(initial_state, None)

        for iteration in range(1000):
            node = self.select(self.root)
            score = self.rollout(node.board)
            self.backpropagate(node, score)

        # pick up the best move in the current position
        try:
            return self.get_best_move(self.root, 0)

        except:
            pass

    def select(self, node):
        while not node.is_terminal:
            if node.is_fully_expanded:
                node = self.get_best_move(node, 2)
            else:
                return self.expand(node)

        return node

    def expand(self, node):
        states = node.board.generate_states()
        for state in states:
            if str(state.position) not in node.children:
                new_node = TreeNode(state, node)
                node.children[str(state.position)] = new_node

                # case when node is fully expanded
                if len(states) == len(node.children):
                    node.is_fully_expanded = True

                # return newly created node
                return new_node

    def rollout(self, board):
        while not board.is_win():
            # try to make a move
            try:
                # make the on board
                board = random.choice(board.generate_states())

            # no moves available
            except:
                # return a draw score
                return 0

        # return score from the player "x" perspective
        if board.player_2 == 'x':
            return 1
        elif board.player_2 == 'o':
            return -1

    def backpropagate(self, node, score):
        while node is not None:
            # update node's visits
            node.visits += 1

            # update node's score
            node.score += score

            # set node to parent
            node = node.parent

    def get_best_move(self, node, exploration_constant):
        # define best score & best moves
        best_score = float('-inf')
        best_moves = []

        # loop over child nodes
        for child_node in node.children.values():
            # define current player
            if child_node.board.player_2 == 'x':
                current_player = 1
            elif child_node.board.player_2 == 'o':
                current_player = -1

            # get move score using UCT formula
            move_score = current_player * child_node.score / child_node.visits + exploration_constant * math.sqrt(
                math.log(node.visits / child_node.visits))

            # better move has been found
            if move_score > best_score:
                best_score = move_score
                best_moves = [child_node]

            # found as good move as already available
            elif move_score == best_score:
                best_moves.append(child_node)

        # return one of the best moves randomly
        return random.choice(best_moves)
