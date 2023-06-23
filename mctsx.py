import math
import random

import ChineseChessBoard


class TreeNode:
    def __init__(self, board: ChineseChessBoard, parent):
        # init associated board state
        self.board = board

        # init is node terminal flag
        if self.board.game_over():
            # we have a terminal node
            self.is_terminal = True

        # otherwise
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
        self.children = []


class Mcts:
    def __init__(self):
        self.root = None

    def search(self, initial_state, num_searches):
        self.root = TreeNode(initial_state, None)

        for _ in range(num_searches):
            node = self.select(self.root)

            score = self.rollout(node.board)

            self.backpropagate(node, score)

            print(f"Loop {_}/{num_searches}")
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
        next_states = node.board.generate_next_states()
        for state in next_states:
            child_node = TreeNode(state[0], node)
            node.children.append(child_node)

        if node.children:
            return random.choice(node.children)
        return None

    def rollout(self, board):
        # Here, you need to implement a function to simulate a complete game
        # and return the final reward based on the rules of Chinese Chess.
        while not board.game_over():
            # You can use a random or lightweight policy to select moves during simulation
            next_state = board.random_move()
            board.move_piece(next_state[0], next_state[1])
        return board.get_final_reward()

    def backpropagate(self, node, score):
        while node is not None:
            # update node's visits
            node.visits += 1

            # update node's score
            node.score += score

            # set node to parent
            node = node.parent

    def get_best_move(self, node, exploration_constant):
        best_score = float('-inf')
        best_moves = []

        for child_node in node.children:
            current_player = 1 if child_node.board.is_red_turn else -1

            move_score = current_player * child_node.score / child_node.visits + exploration_constant * math.sqrt(
                math.log(node.visits / child_node.visits))

            if move_score > best_score:
                best_score = move_score
                best_moves = [child_node]

            # found as good move as already available
            elif move_score == best_score:
                best_moves.append(child_node)

        return random.choice(best_moves)
