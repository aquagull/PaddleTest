import os
os.environ['FLAGS_cinn_new_group_scheduler'] = '1'
os.environ['FLAGS_group_schedule_tiling_first'] = '1'
os.environ['FLAGS_prim_all'] = 'true'
os.environ['FLAGS_prim_enable_dynamic'] = '1'
os.environ['FLAGS_enable_pir_api'] = '1'
os.environ['FLAGS_cinn_bucket_compile'] = '1'

import unittest
import numpy as np
import paddle

def NumCurrentUnittestOperations():
    return 12 # number-of-ops

def GetPaddleDebugNumAllowedOps():
    try:
        return int(os.getenv('PADDLE_DEBUG_NUM_ALLOWED_OPS'))
    except:
        return None

def GetEnvVarEnableJit():
    enable_jit = os.getenv('PADDLE_DEBUG_ENABLE_JIT')
    return enable_jit not in {
        "0",
        "False",
        "false",
        "OFF",
    }

def GetEnvVarEnableCinn():
    enable_cinn = os.getenv('PADDLE_DEBUG_ENABLE_CINN')
    return enable_cinn not in {
        "0",
        "False",
        "false",
        "OFF",
    }


paddle_debug_num_allowed_ops = GetPaddleDebugNumAllowedOps()

def FastReturn(i):
    return (
        type(paddle_debug_num_allowed_ops) is int
        and i >= paddle_debug_num_allowed_ops
    )

class GroupOp(paddle.nn.Layer):
    def __init__(self):
        super().__init__()

    def forward(self, matmul_0, parameter_0):

        if FastReturn(0):
            return matmul_0, parameter_0

        #  type: (-1x-1x5120xf16) <- (-1x-1x5120xf16, 5120xf16)
        # shape: ([S0, S6*S6, 5120]) <- ([S0, S6*S6, 5120], [5120])
        #  data: (None) <- (None, None)
        add_0 = matmul_0 + parameter_0

        if FastReturn(1):
            return add_0

        #  type: (-1x-1x2560xf16) <- (-1x-1x5120xf16)
        # shape: ([S0, S6*S6, 2560]) <- ([S0, S6*S6, 5120])
        #  data: (None) <- (None)
        slice_0 = paddle.slice(add_0, axes=[2], starts=[2560], ends=[5120])

        if FastReturn(2):
            return add_0, slice_0

        #  type: (-1x-1x2560xf16) <- (-1x-1x5120xf16)
        # shape: ([S0, S6*S6, 2560]) <- ([S0, S6*S6, 5120])
        #  data: (None) <- (None)
        slice_1 = paddle.slice(add_0, axes=[2], starts=[0], ends=[2560])

        if FastReturn(3):
            return slice_0, slice_1

        #  type: (xf16) <- ()
        # shape: ([]) <- ()
        #  data: ([0]) <- ()
        full_0 = paddle.full(shape=[], dtype='float16', fill_value=0.5)

        if FastReturn(4):
            return slice_0, slice_1, full_0

        #  type: (xf16) <- ()
        # shape: ([]) <- ()
        #  data: ([1]) <- ()
        full_1 = paddle.full(shape=[], dtype='float16', fill_value=1)

        if FastReturn(5):
            return slice_0, slice_1, full_0, full_1

        #  type: (xf16) <- ()
        # shape: ([]) <- ()
        #  data: ([0]) <- ()
        full_2 = paddle.full(shape=[], dtype='float16', fill_value=0.707107)

        if FastReturn(6):
            return slice_0, slice_1, full_0, full_1, full_2

        #  type: (-1x-1x2560xf16) <- (-1x-1x2560xf16, xf16)
        # shape: ([S0, S6*S6, 2560]) <- ([S0, S6*S6, 2560], [])
        #  data: (None) <- (None, [0])
        multiply_0 = slice_0 * full_2

        if FastReturn(7):
            return slice_0, slice_1, full_0, full_1, multiply_0

        #  type: (-1x-1x2560xf16) <- (-1x-1x2560xf16)
        # shape: ([S0, S6*S6, 2560]) <- ([S0, S6*S6, 2560])
        #  data: (None) <- (None)
        erf_0 = paddle.erf(multiply_0)

        if FastReturn(8):
            return slice_0, slice_1, full_0, full_1, erf_0

        #  type: (-1x-1x2560xf16) <- (xf16, -1x-1x2560xf16)
        # shape: ([S0, S6*S6, 2560]) <- ([], [S0, S6*S6, 2560])
        #  data: (None) <- ([1], None)
        add_1 = full_1 + erf_0

        if FastReturn(9):
            return slice_0, slice_1, full_0, add_1

        #  type: (-1x-1x2560xf16) <- (-1x-1x2560xf16, xf16)
        # shape: ([S0, S6*S6, 2560]) <- ([S0, S6*S6, 2560], [])
        #  data: (None) <- (None, [0])
        multiply_1 = slice_0 * full_0

        if FastReturn(10):
            return slice_1, add_1, multiply_1

        #  type: (-1x-1x2560xf16) <- (-1x-1x2560xf16, -1x-1x2560xf16)
        # shape: ([S0, S6*S6, 2560]) <- ([S0, S6*S6, 2560], [S0, S6*S6, 2560])
        #  data: (None) <- (None, None)
        multiply_2 = multiply_1 * add_1

        if FastReturn(11):
            return slice_1, multiply_2

        #  type: (-1x-1x2560xf16) <- (-1x-1x2560xf16, -1x-1x2560xf16)
        # shape: ([S0, S6*S6, 2560]) <- ([S0, S6*S6, 2560], [S0, S6*S6, 2560])
        #  data: (None) <- (None, None)
        multiply_3 = slice_1 * multiply_2

        #  type: () <- (-1x-1x2560xf16)
        # shape: () <- ([S0, S6*S6, 2560])
        #  data: () <- (None)
        return multiply_3


class TestGroupOp(unittest.TestCase):
    def setUp(self):
        paddle.seed(2024)
        self.prepare_data()

    def prepare_data(self):
        self.inputs = [
            paddle.uniform([2, 2, 5120], dtype='float16', min=-0.5, max=0.5),
            paddle.uniform([5120], dtype='float16', min=-0.5, max=0.5),
        ]
        for input in self.inputs:
          input.stop_gradient = True

    def apply_to_static(self, net, use_cinn):
        build_strategy = paddle.static.BuildStrategy()
        input_spec = [
            paddle.static.InputSpec(shape=[None, None, 5120], dtype='float16'),
            paddle.static.InputSpec(shape=[5120], dtype='float16'),
        ]
        build_strategy.build_cinn_pass = use_cinn
        return paddle.jit.to_static(
            net,
            input_spec=input_spec,
            build_strategy=build_strategy,
            full_graph=True,
        )

    def train(self, use_cinn):
        net = GroupOp()
        net.eval()
        if GetEnvVarEnableJit():
            net = self.apply_to_static(net, use_cinn)
        out = net(*self.inputs)
        return out

    def test_train(self):
        dy_outs = self.train(use_cinn=False)
        cinn_outs = self.train(use_cinn=GetEnvVarEnableCinn())

        for cinn_out, dy_out in zip(cinn_outs, dy_outs):
          if type(cinn_out) is list and type(dy_out) is list:
            for x, y in zip(cinn_out, dy_out):
              self.assert_all_close(x, y)
          else:
            self.assert_all_close(cinn_out, dy_out)

    def assert_all_close(self, x, y):
        if (hasattr(x, "numpy") and hasattr(y, "numpy")):
            np.testing.assert_allclose(x.numpy(), y.numpy(), atol=1e-6)
        else:
            assert x == y


if __name__ == '__main__':
    unittest.main()