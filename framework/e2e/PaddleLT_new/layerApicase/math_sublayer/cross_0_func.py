import numpy as np
import paddle


class LayerCase(paddle.nn.Layer):
    """
    case名称: cross_0
    api简介: 计算张量 x 和 y 在 axis 维度上的向量积（叉积）
    """

    def __init__(self):
        super(LayerCase, self).__init__()

    def forward(self, x, y, ):
        """
        forward
        """
        out = paddle.cross(x, y,  axis=0, )
        return out


def create_tensor_inputs():
    """
    paddle tensor
    """
    inputs = (paddle.to_tensor(-1 + (1 - -1) * np.random.random([3, 4, 4, 3]).astype('float32'), dtype='float32', stop_gradient=False), paddle.to_tensor(-1 + (1 - -1) * np.random.random([3, 4, 4, 3]).astype('float32'), dtype='float32', stop_gradient=False), )
    return inputs


def create_numpy_inputs():
    """
    numpy array
    """
    inputs = (-1 + (1 - -1) * np.random.random([3, 4, 4, 3]).astype('float32'), -1 + (1 - -1) * np.random.random([3, 4, 4, 3]).astype('float32'), )
    return inputs
