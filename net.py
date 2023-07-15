from keras.layers import Conv2D, BatchNormalization, ReLU, Dense, Add, Flatten, Input, Activation
from keras.models import Model

# 定义残差块
class ResBlock(Model):
    def __init__(self, num_filters=256):
        super().__init__()
        self.conv1 = Conv2D(filters=num_filters, kernel_size=3, padding='same')
        self.conv1_bn = BatchNormalization()
        self.conv1_act = Activation('relu')
        self.conv2 = Conv2D(filters=num_filters, kernel_size=3, padding='same')
        self.conv2_bn = BatchNormalization()
        self.conv2_act = Activation('relu')

    def call(self, input_matrix, **kwargs):
        mat = self.conv1(input_matrix)
        mat = self.conv1_bn(mat)
        mat = self.conv1_act(mat)
        mat = self.conv2(mat)
        mat = self.conv2_bn(mat)
        mat = Add()([input_matrix, mat])
        return self.conv2_act(mat)

def create_chinese_chess_model():
    # 定义骨干网络
    inputs = Input(shape=(10, 9, 9))
    x = Conv2D(filters=256, kernel_size=3, strides=1, padding='same')(inputs)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)

    # 定义残差网络
    res_blocks = [ResBlock() for _ in range(13)]
    for res_block in res_blocks:
        x = res_block(x)

    # 策略头
    policy = Conv2D(filters=16, kernel_size=1)(x)
    policy = BatchNormalization()(policy)
    policy = Activation('relu')(policy)
    policy = Flatten()(policy)
    policy = Dense(2086)(policy)

    # 价值头
    value = Conv2D(filters=8, kernel_size=1)(x)
    value = BatchNormalization()(value)
    value = Activation('relu')(value)
    value = Flatten()(value)
    value = Dense(256, activation='relu')(value)
    value = Dense(1, activation='tanh')(value)

    return Model(inputs=inputs, outputs=[policy, value])

if __name__ == '__main__':
    model = create_chinese_chess_model()
    model.summary()
