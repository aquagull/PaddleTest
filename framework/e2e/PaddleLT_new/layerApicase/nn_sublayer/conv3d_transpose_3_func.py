import numpy as np
import paddle


class LayerCase(paddle.nn.Layer):
    """
    case名称: conv3d_transpose_3
    api简介: 2维反卷积
    """

    def __init__(self):
        super(LayerCase, self).__init__()

    def forward(self, x, ):
        """
        forward
        """

        paddle.seed(33)
        np.random.seed(33)
        out = paddle.nn.functional.conv3d_transpose(x,  weight=paddle.to_tensor(-1 + (1 - -1) * np.random.random([3, 1, 3, 3, 3]).astype('float32'), dtype='float32', stop_gradient=False), stride=1, padding=[1, 0, 1], dilation=2, data_format='NCDHW', )
        return out



def create_inputspec(): 
    inputspec = ( 
        paddle.static.InputSpec(shape=(-1, 3, -1, -1, -1), dtype=paddle.float32, stop_gradient=False), 
    )
    return inputspec

def create_tensor_inputs():
    """
    paddle tensor
    """
    inputs = (paddle.to_tensor(-1 + (1 - -1) * np.random.random([2, 3, 2, 2, 2]).astype('float32'), dtype='float32', stop_gradient=False), )
    return inputs


def create_numpy_inputs():
    """
    numpy array
    """
    inputs = (-1 + (1 - -1) * np.random.random([2, 3, 2, 2, 2]).astype('float32'), )
    return inputs

