import numpy as np
import paddle


class LayerCase(paddle.nn.Layer):
    """
    case名称: l1_loss_zero_size_class
    """

    def __init__(self):
        super(LayerCase, self).__init__()

    def forward(self, x, y):
        """
        forward
        """

        paddle.seed(33)
        np.random.seed(33)
        out = paddle.nn.functional.l1_loss(
            x, y,
            reduction='mean',
        )
        return out



def create_inputspec(): 
    inputspec = ( 
        paddle.static.InputSpec(shape=(-1, -1, ), dtype=paddle.float32, stop_gradient=False), 
        paddle.static.InputSpec(shape=(-1, -1, ), dtype=paddle.float32, stop_gradient=False), 
    )
    return inputspec

def create_tensor_inputs():
    """
    paddle tensor
    """
    inputs = (
        paddle.to_tensor(0 + (1 - 0) * np.random.random([10, 0]).astype('float32'), dtype='float32', stop_gradient=False), 
        paddle.to_tensor(0 + (1 - 0) * np.random.random([10, 0]).astype('float32'), dtype='float32', stop_gradient=False),
    )
    return inputs


def create_numpy_inputs():
    """
    numpy array
    """
    inputs = (
        0 + (1 - 0) * np.random.random([10, 0]).astype('float32'), 
        0 + (1 - 0) * np.random.random([10, 0]).astype('float32'), 
    )
    return inputs

