import numpy as np
import paddle


class LayerCase(paddle.nn.Layer):
    """
    case名称: divide_2
    api简介: 输入 x 与输入 y 逐元素相除，并将各个位置的输出元素保存到返回结果中
    """

    def __init__(self):
        super(LayerCase, self).__init__()

    def forward(self, x, y, ):
        """
        forward
        """
        out = paddle.divide(x, y,  )
        return out


def create_tensor_inputs():
    """
    paddle tensor
    """
    inputs = ()
    return inputs


def create_numpy_inputs():
    """
    numpy array
    """
    inputs = (paddle.to_tensor([-0.1, 2], dtype='float32', stop_gradient=False), paddle.to_tensor([-0.1, 2], dtype='float32', stop_gradient=False), )
    return inputs
