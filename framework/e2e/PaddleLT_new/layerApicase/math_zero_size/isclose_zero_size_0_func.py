import numpy as np
import paddle


class LayerCase(paddle.nn.Layer):
    """
    case名称: isclose_zero_size_func
    """

    def __init__(self):
        super(LayerCase, self).__init__()

    def forward(self, x, y):
        """
        forward
        """

        paddle.seed(33)
        np.random.seed(33)
        out = paddle.isclose(x, y, rtol=0.00001, atol=0.00000001, equal_nan=false )
        return out



def create_inputspec(): 
    inputspec = ( 
        paddle.static.InputSpec(shape=(-1, -1, -1), dtype=paddle.float32, stop_gradient=False), 
        paddle.static.InputSpec(shape=(-1, -1, -1), dtype=paddle.float32, stop_gradient=False), 
    )
    return inputspec

def create_tensor_inputs():
    """
    paddle tensor
    """
    inputs = (
        paddle.to_tensor(-1 + 2 * np.random.random([128, 0, 1]).astype('float32'), dtype='float32', stop_gradient=False), 
        paddle.to_tensor(-1 + 2 * np.random.random([128, 0, 1]).astype('float32'), dtype='float32', stop_gradient=False),
    )
    return inputs


def create_numpy_inputs():
    """
    numpy array
    """
    inputs = (
        (-1 + 2 * np.random.random([128, 0, 1])).astype('float32'), 
        (-1 + 2 * np.random.random([128, 0, 1])).astype('float32'), 
    )
    return inputs

