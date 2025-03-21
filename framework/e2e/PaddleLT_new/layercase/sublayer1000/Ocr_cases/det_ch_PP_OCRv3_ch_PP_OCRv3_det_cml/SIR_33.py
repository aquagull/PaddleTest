# method:__sub__||method:__rmul__||api:paddle.tensor.ops.exp||method:__radd__||api:paddle.tensor.ops.reciprocal||api:paddle.tensor.manipulation.concat
import paddle
import unittest
import numpy as np


class LayerCase(paddle.nn.Layer):
    def __init__(self):
        super().__init__()
    def forward(
        self,
        var_0,    # (shape: [2, 1, 960, 960], dtype: paddle.float32, stop_gradient: False)
        var_1,    # (shape: [2, 1, 960, 960], dtype: paddle.float32, stop_gradient: False)
    ):
        var_2 = var_1.__sub__(var_0)
        var_3 = var_2.__rmul__(-50)
        var_4 = paddle.tensor.ops.exp(var_3)
        var_5 = var_4.__radd__(1)
        var_6 = paddle.tensor.ops.reciprocal(var_5)
        var_7 = paddle.tensor.manipulation.concat([var_1, var_0, var_6], axis=1)
        return var_7



def create_inputspec(): 
    inputspec = ( 
        paddle.static.InputSpec(shape=(-1, -1, -1, -1), dtype=paddle.float32, stop_gradient=False), 
        paddle.static.InputSpec(shape=(-1, -1, -1, -1), dtype=paddle.float32, stop_gradient=False), 
    )
    return inputspec

def create_tensor_inputs():
    inputs = (
        paddle.rand(shape=[2, 1, 960, 960], dtype=paddle.float32),
        paddle.rand(shape=[2, 1, 960, 960], dtype=paddle.float32),
    )
    return inputs


def create_numpy_inputs():
    inputs = (
        np.random.random(size=[2, 1, 960, 960]).astype('float32'),
        np.random.random(size=[2, 1, 960, 960]).astype('float32'),
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