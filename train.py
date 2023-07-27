import numpy as np
from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import TensorBoard
import time
import matplotlib.pyplot as plt
from tensorflow.keras.callbacks import Callback
from tensorflow.keras.models import load_model

from net import create_chinese_chess_model

# 定义优化器和损失函数
optimizer = Adam()
loss_fn = MeanSquaredError()


def split_input_line(line):
    # 找到第一个，倒数第二个和最后一个逗号的位置
    first_comma = line.find(',')
    second_last_comma = line.rfind(',', 0, line.rfind(','))
    last_comma = line.rfind(',')

    # 获取棋盘状态、移动、结果和走棋方
    board_state = line[:first_comma].strip()
    move_str = line[first_comma + 1:second_last_comma].strip()
    outcome = int(line[second_last_comma + 1:last_comma].strip())
    player = int(line[last_comma + 1:].strip())

    # 处理移动字符串，将其转换为两个元组
    move_str = move_str.replace('(', '').replace(')', '')
    move_parts = move_str.split(',')
    move = ((int(move_parts[0]), int(move_parts[1])), (int(move_parts[2]), int(move_parts[3])))

    return board_state, move, outcome, player


def to_tensor(line):
    board_state, move, outcome, turn = split_input_line(line)

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
            tensor[i, j, :7] = piece_to_onehot[board_state[i * 9 + j]]

    # fill in the tensor with the last move
    if move is not None:
        source, target = move
        if source is not None and target is not None:
            if source[0] != -1 and source[1] != -1 and target[0] != -1 and target[1] != -1:
                tensor[source[0], source[1], 7] = -1
                tensor[target[0], target[1], 7] = 1

    # fill in the tensor with the current turn
    tensor[:, :, 8] = turn

    return tensor, outcome


# 创建模型
model = load_model("model_wukong_v16.h5")
model.compile(optimizer=optimizer, loss=loss_fn)

# 读取和准备数据
data = []
labels = []
with open('E:\\myprojects\\crawl\\ccbridge_arena\\qipu_from_ccbridge_arena_result.txt', 'r') as f:
    for line in f:
        input_data, label = to_tensor(line)
        data.append(input_data)
        labels.append(label)

data = np.array(data)
labels = np.array(labels)


class PlotLosses(Callback):
    def on_train_begin(self, logs={}):
        self.i = 0
        self.x = []
        self.losses = []
        self.fig = plt.figure()

        self.logs = []

    def on_epoch_end(self, epoch, logs={}):
        self.logs.append(logs)
        self.x.append(self.i)
        self.losses.append(logs.get('loss'))
        self.i += 1

        plt.plot(self.x, self.losses, label="loss")
        plt.legend()
        plt.show()


class CustomSaver(Callback):
    def on_epoch_end(self, epoch, logs={}):
        if epoch % 4 == 0:  # or save after some epoch, each k-th epoch etc.
            filename = 'model_v' + str(epoch) + '.h5'
            self.model.save(filename)


saver = CustomSaver()
plot_losses = PlotLosses()

# 训练模型
model.fit(data, labels, epochs=20, batch_size=512, callbacks=[plot_losses, saver])
model.save("model_wukong_arena_20epoch.h5")

