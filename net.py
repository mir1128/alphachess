import tensorflow as tf
from tensorflow.keras.layers import Input, Conv2D, Flatten, Dense, Softmax, Add
from tensorflow.keras.models import Model


def create_chinese_chess_model():
    input_shape = (10, 9, 9)  # 9 channels for the board representation
    num_moves = 2086  # The total number of possible moves in Chinese Chess

    input_tensor = Input(shape=input_shape)
    x = Conv2D(64, kernel_size=3, padding='same', activation='relu')(input_tensor)
    x = Conv2D(64, kernel_size=3, padding='same', activation='relu')(x)
    x = Conv2D(64, kernel_size=3, padding='same', activation='relu')(x)

    x = Flatten()(x)
    x = Dense(256, activation='relu')(x)

    policy_head = Dense(num_moves, activation='softmax', name='policy_head')(x)
    value_head = Dense(1, activation='tanh', name='value_head')(x)

    model = Model(inputs=input_tensor, outputs=[policy_head, value_head])
    return model


model = create_chinese_chess_model()
model.summary()