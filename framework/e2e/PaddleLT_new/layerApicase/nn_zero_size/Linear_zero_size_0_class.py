import numpy as np
import paddle


class LayerCase(paddle.nn.Layer):
    """
    case名称: Linear_zero_size_class
    """

    def __init__(self):
        super(LayerCase, self).__init__()
        self.func = paddle.nn.Linear(in_features=10, out_features=0)

    def forward(self, data, ):
        """
        forward
        """

        paddle.seed(33)
        np.random.seed(33)
        out = self.func(data, )
        return out



def create_inputspec(): 
    inputspec = ( 
        paddle.static.InputSpec(shape=(-1, 0), dtype=paddle.float32, stop_gradient=False), 
    )
    return inputspec

def create_tensor_inputs():
    """
    paddle tensor
    """
    inputs = (paddle.to_tensor(-1 + (1 - -1) * np.random.random([10, 0]).astype('float32'), dtype='float32', stop_gradient=False), )
    return inputs


def create_numpy_inputs():
    """
    numpy array
    """
    inputs = (-1 + (1 - -1) * np.random.random([10, 0]).astype('float32'), )
    return inputs

