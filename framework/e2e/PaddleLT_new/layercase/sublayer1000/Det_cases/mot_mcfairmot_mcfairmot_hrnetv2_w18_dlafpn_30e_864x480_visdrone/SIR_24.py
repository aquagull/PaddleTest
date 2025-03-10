# api:paddle.tensor.linalg.transpose||api:paddle.tensor.manipulation.reshape||api:paddle.tensor.manipulation.unsqueeze||api:paddle.tensor.creation.full||api:paddle.tensor.manipulation.concat||api:paddle.tensor.manipulation.concat||api:paddle.tensor.manipulation.gather_nd||api:paddle.tensor.manipulation.unsqueeze||api:paddle.tensor.manipulation.expand_as||method:__gt__||api:paddle.tensor.search.masked_select||api:paddle.tensor.manipulation.reshape
import paddle
import unittest
import numpy as np


class LayerCase(paddle.nn.Layer):
    def __init__(self):
        super().__init__()
    def forward(
        self,
        var_0,    # (shape: [1, 128, 120, 216], dtype: paddle.float32, stop_gradient: False)
        var_1,    # (shape: [1, 500], dtype: paddle.int64, stop_gradient: True)
        var_2,    # (shape: [1, 500], dtype: paddle.int32, stop_gradient: True)
    ):
        var_3 = paddle.tensor.linalg.transpose(var_0, perm=[0, 2, 3, 1])
        var_4 = paddle.tensor.manipulation.reshape(var_3, shape=[1, -1, 128])
        var_5 = paddle.tensor.manipulation.unsqueeze(var_1, 2)
        var_6 = paddle.tensor.creation.full(shape=[1, 500, 1], fill_value=0, dtype='int64')
        var_7 = paddle.tensor.manipulation.concat([var_6], axis=0)
        var_8 = paddle.tensor.manipulation.concat(x=[var_7, var_5], axis=2)
        var_9 = paddle.tensor.manipulation.gather_nd(var_4, index=var_8)
        var_10 = paddle.tensor.manipulation.unsqueeze(var_2, axis=2)
        var_11 = paddle.tensor.manipulation.expand_as(var_10, var_9)
        var_12 = var_11.__gt__(0)
        var_13 = paddle.tensor.search.masked_select(var_9, var_12)
        var_14 = paddle.tensor.manipulation.reshape(var_13, shape=[-1, 128])
        return var_8, var_14



def create_inputspec(): 
    inputspec = ( 
        paddle.static.InputSpec(shape=(-1, -1, -1, -1), dtype=paddle.float32, stop_gradient=False), 
        paddle.static.InputSpec(shape=(-1, -1), dtype=paddle.int64, stop_gradient=False), 
        paddle.static.InputSpec(shape=(-1, -1), dtype=paddle.int32, stop_gradient=False), 
    )
    return inputspec

def create_tensor_inputs():
    inputs = (
        paddle.rand(shape=[1, 128, 120, 216], dtype=paddle.float32),
        paddle.randint(low=0, high=10, shape=[1, 500], dtype=paddle.int64),
        paddle.randint(low=0, high=10, shape=[1, 500], dtype=paddle.int32),
    )
    return inputs


def create_numpy_inputs():
    inputs = (
        np.random.random(size=[1, 128, 120, 216]).astype('float32'),
        np.random.randint(low=0, high=10, size=[1, 500], dtype='int64'),
        np.random.randint(low=0, high=10, size=[1, 500], dtype='int32'),
    )
    return inputs


class TestLayer(unittest.TestCase):
    def setUp(self):
        self.inputs = create_tensor_inputs()
        self.net = LayerCase()
    def train(self, net, to_static, with_prim=False, with_cinn=False):
        if to_static:
            paddle.set_flags({'FLAGS_prim_all': with_prim})
            if with_cinn:
                build_strategy = paddle.static.BuildStrategy()
                build_strategy.build_cinn_pass = True
                net = paddle.jit.to_static(net, build_strategy=build_strategy, full_graph=True)
            else:
                net = paddle.jit.to_static(net, full_graph=True)
        paddle.seed(123)
        outs = net(*self.inputs)
        return outs
    def test_ast_prim_cinn(self):
        st_out = self.train(self.net, to_static=True)
        cinn_out = self.train(self.net, to_static=True, with_prim=True, with_cinn=True)
        for st, cinn in zip(paddle.utils.flatten(st_out), paddle.utils.flatten(cinn_out)):
            np.testing.assert_allclose(st.numpy(), cinn.numpy(), atol=1e-8)


if __name__ == '__main__':
    unittest.main()