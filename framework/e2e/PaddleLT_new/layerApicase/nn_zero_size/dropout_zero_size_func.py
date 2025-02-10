import numpy as np
import paddle


class LayerCase(paddle.nn.Layer):
    """
    case名称: dropout_zero_size_func
    """

    def __init__(self):
        super(LayerCase, self).__init__()

    def forward(self, data, ):
        """
        forward
        """

        paddle.seed(33)
        np.random.seed(33)
        out = paddle.nn.functional.dropout(data, p=0.5)
        return out



def create_inputspec(): 
    inputspec = ( 
        paddle.static.InputSpec(shape=(-1, 0, -1, -1), dtype=paddle.float32, stop_gradient=False), 
    )
    return inputspec

def create_tensor_inputs():
    """
    paddle tensor
    """
    inputs = (paddle.to_tensor(-1 + (1 - -1) * np.random.random([12, 0, 10, 10]).astype('float32'), dtype='float32', stop_gradient=False), )
    return inputs


def create_numpy_inputs():
    """
    numpy array
    """
    inputs = (-1 + (1 - -1) * np.random.random([12, 0, 10, 10]).astype('float32'), )
    return inputs

