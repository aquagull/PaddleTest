import numpy as np
import paddle


class LayerCase(paddle.nn.Layer):
    """
    case名称: multiply_0
    api简介: 逐元素相乘算子，输入 x 与输入 y 逐元素相乘，并将各个位置的输出元素保存到返回结果中
    """

    def __init__(self):
        super(LayerCase, self).__init__()

    def forward(self, x, y, ):
        """
        forward
        """

        paddle.seed(33)
        np.random.seed(33)
        out = paddle.multiply(x, y,  )
        return out


def create_tensor_inputs():
    """
    paddle tensor
    """
    inputs = (paddle.to_tensor(-1 + (1 - -1) * np.random.random([1, 2, 1, 3]).astype('float32'), dtype='float32', stop_gradient=False), paddle.to_tensor(-1 + (1 - -1) * np.random.random([1, 2, 3]).astype('float32'), dtype='float32', stop_gradient=False), )
    return inputs


def create_numpy_inputs():
    """
    numpy array
    """
    inputs = (-1 + (1 - -1) * np.random.random([1, 2, 1, 3]).astype('float32'), -1 + (1 - -1) * np.random.random([1, 2, 3]).astype('float32'), )
    return inputs

