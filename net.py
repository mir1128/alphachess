import tensorflow as tf
from keras import layers, models


def create_chinese_chess_model():
    input_shape = (9, 10, 9)

    model = models.Sequential()

    # 第一个卷积层
    model.add(layers.Conv2D(32, kernel_size=(3, 3), padding='same', activation='relu', input_shape=input_shape))
    model.add(layers.BatchNormalization())

    # 第二个卷积层
    model.add(layers.Conv2D(64, kernel_size=(3, 3), padding='same', activation='relu'))
    model.add(layers.BatchNormalization())

    # 第三个卷积层
    model.add(layers.Conv2D(128, kernel_size=(3, 3), padding='same', activation='relu'))
    model.add(layers.BatchNormalization())

    # 池化层
    model.add(layers.MaxPooling2D(pool_size=(2, 2)))

    # 展平
    model.add(layers.Flatten())

    # 全连接层
    model.add(layers.Dense(256, activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.Dropout(0.5))

    # 输出层，预测动作值
    model.add(layers.Dense(1, activation='tanh'))

    return model


model = create_chinese_chess_model()
model.summary()