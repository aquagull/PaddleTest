import numpy as np
import paddle


class LayerCase(paddle.nn.Layer):
    """
    case名称: Multinomial_zero_size_func
    """

    def __init__(self):
        super(LayerCase, self).__init__()

    def forward(self, ):
        """
        forward
        """

        paddle.seed(33)
        np.random.seed(33)
        out = paddle.distribution.Multinomial(total_count=10, probs=paddle.to_tensor([0.2, 0.3, 0.5], dtype='float32')).sample(shape=[10, 0])
        return out



def create_inputspec(): 
    inputspec = ()
    return inputspec

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
    inputs = ()
    return inputs

