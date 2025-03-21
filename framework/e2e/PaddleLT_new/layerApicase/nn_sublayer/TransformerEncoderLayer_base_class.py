import numpy as np
import paddle


class LayerCase(paddle.nn.Layer):
    """
    case名称: TransformerEncoderLayer_base
    api简介: Transformer编码器层
    """

    def __init__(self):
        super(LayerCase, self).__init__()
        self.func = paddle.nn.TransformerEncoderLayer(d_model=128, nhead=2, dim_feedforward=512, dropout=0.1, activation='relu', )

    def forward(self, data0, data1, ):
        """
        forward
        """

        paddle.seed(33)
        np.random.seed(33)
        out = self.func(data0, data1, )
        return out



def create_inputspec(): 
    inputspec = ( 
        paddle.static.InputSpec(shape=(2, 4, -1), dtype=paddle.float32, stop_gradient=False), 
        paddle.static.InputSpec(shape=(-1, -1, -1, -1), dtype=paddle.float32, stop_gradient=False), 
    )
    return inputspec

def create_tensor_inputs():
    """
    paddle tensor
    """
    inputs = (paddle.to_tensor(-1 + (1 - -1) * np.random.random([2, 4, 128]).astype('float32'), dtype='float32', stop_gradient=False), paddle.to_tensor(-1 + (1 - -1) * np.random.random([2, 2, 4, 4]).astype('float32'), dtype='float32', stop_gradient=False), )
    return inputs


def create_numpy_inputs():
    """
    numpy array
    """
    inputs = (-1 + (1 - -1) * np.random.random([2, 4, 128]).astype('float32'), -1 + (1 - -1) * np.random.random([2, 2, 4, 4]).astype('float32'), )
    return inputs

