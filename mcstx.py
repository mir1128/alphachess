import concurrent.futures
import math
import random
import threading

import numpy as np

from ChineseChessBoard import ChineseChessBoard


class TreeNode:
    def __init__(self, board: ChineseChessBoard, parent, source, target, policy_pred=None):
        # init associated board state
        self.board = board
        self.source = source
        self.target = target
        # 概率
        self.probability = policy_pred

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

        # virtual loss
        self.virtual_loss = 0

        # for parallel search
        self.lock = threading.RLock()


class Mcst:
    def __init__(self, model):
        self.root = None
        self.model = model

    def update_root(self, source, target):
        # Find the child node corresponding to the selected move
        for child in self.root.children:
            if child.source == source and child.target == target:
                self.root = child
                self.root.parent = None
                return
        # If the move was not in the children of the root
        # (which should not happen if the tree search is working correctly),
        # fall back to creating a new tree
        self.root = TreeNode(self.root.board.copy(), None, source, target, None)

    def start(self, initial_state, num_searches):

        print(f"start search {num_searches} times.")

        self.root = TreeNode(initial_state, None, None, None, None)

        for _ in range(num_searches):
            node = self.select(self.root)
            self.backpropagate(node)
            print(f"Loop {_ + 1}/{num_searches}")
        try:
            return self.get_best_move(self.root, 0)
        except:
            pass

    def search(self, num_searches):
        print(f"search count: {num_searches}")
        for _ in range(num_searches):
            node = self.select(self.root)
            self.backpropagate(node)

            # print(f"Loop {_ + 1}/{num_searches}")

        try:
            return self.get_best_move(self.root, 0)
        except:
            pass

    def select(self, node):
        while not node.is_terminal:
            if node.is_fully_expanded:
                node = self.get_best_move(node, 2)
                with node.lock:
                    node.virtual_loss += 1
            else:
                return self.expand(node)
        return node

    def expand(self, node):
        with node.lock:
            next_states = node.board.generate_next_states()

            # Get the policy and value predictions from the neural network
            state_tensor = to_tensor(node)
            policy_pred, value_pred = self.model.predict(np.expand_dims(state_tensor, axis=0))
            policy_pred = np.squeeze(policy_pred, axis=0)

            for i, next_state in enumerate(next_states):
                board, src, dst = next_state
                probability = get_probability(src, dst, policy_pred)
                child_node = TreeNode(board.copy(), node, src, dst, probability)

                # Set the value of the node to the value prediction from the neural network
                child_node.score = value_pred.item()

                node.children.append(child_node)

            node.is_fully_expanded = True

            if node.children:
                # Select the child with the highest prior probability from the policy head
                best_child = max(node.children, key=lambda child: child.probability)
                return best_child
            return None

    def rollout(self, board):
        # Here, you need to implement a function to simulate a complete game
        # and return the final reward based on the rules of Chinese Chess.
        while not board.game_over():
            # You can use a random or lightweight policy to select moves during simulation
            next_state = board.random_move()

            # print(board.encode())

            board.move_piece(next_state[0], next_state[1])
        return board.get_final_reward()

    def backpropagate(self, node):
        if node is None or node.probability is None:
            return

        with node.lock:
            node.visits += 1
            node.virtual_loss -= 1  # 搜索完成后把虚拟损失加回来
            prev = node.parent
        while prev is not None:
            with prev.lock:
                prev.visits += 1
                prev.virtual_loss -= 1  # 搜索完成后把虚拟损失加回来
                prev.score += node.score

            prev = prev.parent

    def get_best_move(self, node, exploration_constant):
        best_score = float('-inf')
        best_moves = []

        try:
            for child_node in node.children:
                current_player = 1 if child_node.board.is_red_turn else -1

                # puct = (score / N_i) + p * sqrt(total)/ (N_i + 1)
                exploitation = (current_player * child_node.score / child_node.visits) if child_node.visits > 0 else 0

                exploration_constant = exploration_constant / math.sqrt(1 + child_node.visits)
                exploration = exploration_constant * child_node.probability * math.sqrt(node.visits) / (
                            1 + child_node.visits)

                move_score = exploitation + exploration

                if move_score > best_score:
                    best_score = move_score
                    best_moves = [child_node]

                # found as good move as already available
                elif move_score == best_score:
                    best_moves.append(child_node)

            return random.choice(best_moves)
        except Exception as e:
            print("An exception occurred: ", e)

    def parallel_start(self, initial_state, num_searches):
        print(f"start search {num_searches} times.")
        self.root = TreeNode(initial_state, None, None, None, None)

        return self.parallel_search(num_searches)

    def parallel_search(self, num_searches):
        print(f"search count: {num_searches}")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.search_once) for _ in range(num_searches)]
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                print(f"Loop {i + 1}/{num_searches}")

        try:
            return self.get_best_move(self.root, 0)
        except Exception as e:
            print("An exception occurred: ", e)

    def search_once(self):
        node = self.select(self.root)
        self.backpropagate(node)


def create_uci_labels():
    labels_array = []
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    Advisor_labels = ['d7e8', 'e8d7', 'e8f9', 'f9e8', 'd0e1', 'e1d0', 'e1f2', 'f2e1',
                      'd2e1', 'e1d2', 'e1f0', 'f0e1', 'd9e8', 'e8d9', 'e8f7', 'f7e8']
    Bishop_labels = ['a2c4', 'c4a2', 'c0e2', 'e2c0', 'e2g4', 'g4e2', 'g0i2', 'i2g0',
                     'a7c9', 'c9a7', 'c5e7', 'e7c5', 'e7g9', 'g9e7', 'g5i7', 'i7g5',
                     'a2c0', 'c0a2', 'c4e2', 'e2c4', 'e2g0', 'g0e2', 'g4i2', 'i2g4',
                     'a7c5', 'c5a7', 'c9e7', 'e7c9', 'e7g5', 'g5e7', 'g9i7', 'i7g9']

    for l1 in range(9):
        for n1 in range(10):
            destinations = [(t, n1) for t in range(9)] + \
                           [(l1, t) for t in range(10)] + \
                           [(l1 + a, n1 + b) for (a, b) in
                            [(-2, -1), (-1, -2), (-2, 1), (1, -2), (2, -1), (-1, 2), (2, 1), (1, 2)]]  # 马走日
            for (l2, n2) in destinations:
                if (l1, n1) != (l2, n2) and l2 in range(9) and n2 in range(10):
                    move = letters[l1] + numbers[n1] + letters[l2] + numbers[n2]
                    labels_array.append(move)

    for p in Advisor_labels:
        labels_array.append(p)

    for p in Bishop_labels:
        labels_array.append(p)

    return labels_array


def to_uci_label(src, dst):
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    # Convert the source and destination tuples to UCI labels
    # Reverse the order of the coordinates to match the UCI format
    uci_label = letters[src[1]] + numbers[9 - src[0]] + letters[dst[1]] + numbers[9 - dst[0]]

    return uci_label


uci_labels = create_uci_labels()


def get_probability(src, dst, policy_pred):
    # Convert the source and destination coordinates to a UCI label
    uci_label = to_uci_label(src, dst)

    # Create the UCI labels array
    # Find the index of the UCI label in the labels array
    label_index = uci_labels.index(uci_label)

    # Get the probability from the policy prediction vector
    probability = policy_pred[label_index]

    return probability


def to_tensor(node: TreeNode):
    # one-hot representation for each piece
    brd = node.board
    turn = 1 if brd.is_red_turn else 0

    parent = node.parent
    last_step = (parent.source, parent.target) if parent is not None else None

    piece_to_onehot = {
        'R': np.array([1, 0, 0, 0, 0, 0, 0]),
        'N': np.array([0, 1, 0, 0, 0, 0, 0]),
        'B': np.array([0, 0, 1, 0, 0, 0, 0]),
        'A': np.array([0, 0, 0, 1, 0, 0, 0]),
        'K': np.array([0, 0, 0, 0, 1, 0, 0]),
        'C': np.array([0, 0, 0, 0, 0, 1, 0]),
        'P': np.array([0, 0, 0, 0, 0, 0, 1]),
        'r': np.array([-1, 0, 0, 0, 0, 0, 0]),
        'n': np.array([0, -1, 0, 0, 0, 0, 0]),
        'b': np.array([0, 0, -1, 0, 0, 0, 0]),
        'a': np.array([0, 0, 0, -1, 0, 0, 0]),
        'k': np.array([0, 0, 0, 0, -1, 0, 0]),
        'c': np.array([0, 0, 0, 0, 0, -1, 0]),
        'p': np.array([0, 0, 0, 0, 0, 0, -1]),
        '_': np.array([0, 0, 0, 0, 0, 0, 0])
    }

    # create an empty tensor
    tensor = np.zeros((10, 9, 9))  # the dimension of the tensor is (10, 9, 9)

    # fill in the tensor with one-hot encoding of the pieces
    for i in range(10):
        for j in range(9):
            tensor[i, j, :7] = piece_to_onehot[brd.board[i][j]]

    # fill in the tensor with the last move
    if last_step is not None:
        source, target = last_step
        if source is not None and target is not None:
            tensor[source[0], source[1], 7] = -1
            tensor[target[0], target[1], 7] = 1

    # fill in the tensor with the current turn
    tensor[:, :, 8] = turn

    return tensor


def test_to_tensor():
    test_board = ChineseChessBoard()
    # Create a root node
    root = TreeNode(test_board, None, None, None)

    for _ in range(5):
        test_board = test_board.copy()
        move = test_board.random_move()
        test_board.move_piece(*move)

        node = TreeNode(test_board, root, *move)

        print(test_board.encode())
        tensor = to_tensor(node)
        root = node


def test_uci():
    assert to_uci_label((0, 4), (1, 4)) == 'e9e8', "Error in test case 1"
    assert to_uci_label((0, 0), (0, 1)) == 'a9b9', "Error in test case 2"
    assert to_uci_label((0, 1), (2, 2)) == 'b9c7', "Error in test case 3"
    assert to_uci_label((2, 1), (5, 1)) == 'b7b4', "Error in test case 4"
    assert to_uci_label((3, 0), (4, 0)) == 'a6a5', "Error in test case 5"


if __name__ == '__main__':
    test_to_tensor()
    test_uci()
    exit()
