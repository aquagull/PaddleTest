import numpy as np
import paddle


class LayerCase(paddle.nn.Layer):
    """
    case名称: strided_slice_0
    api简介: 沿多个轴生成 input 的切片
    """

    def __init__(self):
        super(LayerCase, self).__init__()

    def forward(self, x, ):
        """
        forward
        """

        paddle.seed(33)
        np.random.seed(33)
        out = paddle.strided_slice(x,  axes=[1, 2, 3], starts=[-3, 0, 2], ends=[3, 2, 4], strides=[1, 1, 1], )
        return out



def create_inputspec(): 
    inputspec = ( 
        paddle.static.InputSpec(shape=(-1, -1, -1, -1), dtype=paddle.float32, stop_gradient=False), 
    )
    return inputspec

def create_tensor_inputs():
    """
    paddle tensor
    """
    inputs = (paddle.to_tensor(-1 + (1 - -1) * np.random.random([3, 4, 5, 6]).astype('float32'), dtype='float32', stop_gradient=False), )
    return inputs


def create_numpy_inputs():
    """
    numpy array
    """
    inputs = (-1 + (1 - -1) * np.random.random([3, 4, 5, 6]).astype('float32'), )
    return inputs

