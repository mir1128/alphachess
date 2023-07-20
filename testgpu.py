import tensorflow as tf
import numpy as np

print(tf.test.is_gpu_available())
gpu_device_name = tf.test.gpu_device_name()
print(gpu_device_name)
