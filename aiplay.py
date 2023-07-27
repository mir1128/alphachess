from tensorflow.keras.models import load_model

from ChineseChessBoard import ChineseChessBoard
from log.logger import logger
from mcstx import Mcst
import datetime


def ai_play_one_round(neural_model, search_number):
    board = ChineseChessBoard()
    game_record = []

    mcst = Mcst(neural_model)
    node = mcst.start(board, search_number)

    print(f"red from {node.source} to {node.target}")

    if node is None or node.source is None or node.target is None:
        logger.info("return error node %s", str(node))
        return None

    while not node.board.is_game_over:
        game_record.append((node.board.copy(), (node.source, node.target)))

        next_board = node.board.copy()
        next_board.move_piece(node.source, node.target)

        mcst.update_root(node.source, node.target)

        turn = "red" if node.board.is_red_turn else "black"

        node = mcst.search(search_number - mcst.root.visits)

        print(f"{turn} from {node.source} to {node.target}")

        if node is None or node.source is None or node.target is None:
            logger.info("return error node %s", str(node))
            return None

    # save the result of the game
    winner = 1 if node.board.winner == 'red' else -1 if node.board.winner == 'black' else 0
    game_record = [(record[0], record[1], winner) for record in game_record]

    return game_record


def save_game_record(game_record, filename):
    """Append the game record to a file."""
    with open(filename, 'a') as f:
        for record in game_record:
            f.write(str(record[0].encode()) + "," + str(record[1]) + "," + str(record[2]) + '\n')
        f.write("-----------\n")


def ai_play(neural_model, search_number, rounds, filename_prefix):
    """Let the AI play multiple rounds of game and save the records."""
    # Create an initial filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.txt"

    for i in range(1, rounds + 1):
        game_record = ai_play_one_round(neural_model, search_number)
        print(f"rounds: {i + 1}/{rounds}, timestamp: ", timestamp)

        # Create a new file for every 100 games
        if i % 100 == 0:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.txt"

        save_game_record(game_record, filename)


if __name__ == '__main__':
    ai_play(load_model('model.h5'), 1000, 1000, "records/record")
    exit()
