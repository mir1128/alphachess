import concurrent.futures
import math
import random

from GameInterface import GameInterface


class MCTSNode:
    def __init__(self, state: (GameInterface, None, None), parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visit_count = 0
        self.total_reward = 0


class MCTS:
    def __init__(self, game: (GameInterface, None, None), c=1.0):
        self.root = MCTSNode(game)
        self.c = c

    def ucb1(self, node):
        exploitation = node.total_reward / node.visit_count if node.visit_count > 0 else 0
        exploration = math.sqrt(
            2 * math.log(node.parent.visit_count) / node.visit_count) if node.visit_count > 0 else float("inf")
        return exploitation + self.c * exploration

    def selection(self, node):
        best_child = max(node.children, key=self.ucb1)
        return best_child

    def expansion(self, node):
        # Here, you need to implement a function to generate all possible next states
        # based on the rules of Chinese Chess and add them as children to the node.

        chess_board = node.state[0]
        next_states = chess_board.generate_next_states()
        for state in next_states:
            child_node = MCTSNode(state, parent=node)
            node.children.append(child_node)

    def simulation(self, chess_board):
        # Here, you need to implement a function to simulate a complete game
        # and return the final reward based on the rules of Chinese Chess.
        while not chess_board.game_over():
            # You can use a random or lightweight policy to select moves during simulation
            next_state = chess_board.random_move()
            state = next_state
        return chess_board.get_final_reward()

    def backpropagation(self, node, reward):
        while node is not None:
            node.visit_count += 1
            node.total_reward += reward
            reward = -reward  # Invert the reward for the opponent's perspective
            node = node.parent

    def parallel_search(self, node, num_searches, num_threads):
        # Divide searches equally among threads
        searches_per_thread = [num_searches // num_threads] * num_threads
        for i in range(num_searches % num_threads):
            searches_per_thread[i] += 1

        # Run searches in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(self.search, node, num) for num in searches_per_thread]

            # Wait for all threads to finish and retrieve results
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # Update the root node with the results from all threads
        for result in results:
            self.backpropagation(node, result)

    def search(self, num_searches):
        for _ in range(num_searches):
            # Perform one search starting from the given node
            leaf_node = self.tree_policy()
            reward = self.simulation(leaf_node.state[0])
            self.backpropagation(leaf_node, reward)

            print(f"Loop {_}/{num_searches}")

        # Find the best move based on the visit count of the children
        best_child = max(self.root.children, key=lambda node: node.visit_count)
        return best_child.state

    def execute_best_move(self):
        # Get the best move using the search method
        best_move = self.search(1000)

        # Update the root of the tree to the new state
        self.root = best_move

    def tree_policy(self):
        # Traverse the tree from the given node to a leaf node using selection and expansion
        node = self.root
        while not node.state[0].game_over():
            if node.children:
                node = self.selection(node)
            else:
                self.expansion(node)
                if node.children:
                    node = random.choice(node.children)
                else:
                    break  # No legal moves left, reached a terminal state
        return node
