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
    return 5 # number-of-ops

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

    def forward(self, group_0, group_1, matmul_0, triu_0):

        if FastReturn(0):
            return group_0, group_1, matmul_0, triu_0

        #  type: (4xi64) <- (-1x-1x768xf16, -1x-1x64xf16)
        # shape: ([4]) <- ([S0, S1, 768], [S0*12, S1, 64])
        #  data: ([S0, 12, S1, S1]) <- (None, None)
        generate_shape_0 = [group_0.shape[0], 12, group_1.shape[1], group_1.shape[1]] # inputs: group_0, group_1

        if FastReturn(1):
            return group_0, group_1, matmul_0, triu_0, generate_shape_0

        #  type: (-1x12x-1x-1xf16, 0x-1x-1x-1xf16) <- (-1x-1x-1xf16, 4xi64)
        # shape: ([S0, 12, S1, S1], [0, S0*12, S1, S1]) <- ([S0*12, S1, S1], [4])
        #  data: (None, None) <- (None, [S0, 12, S1, S1])
        reshape_0, reshape_1 = paddle.reshape(matmul_0, generate_shape_0), None

        if FastReturn(2):
            return group_0, group_1, triu_0, reshape_0

        #  type: (-1x12x-1x-1xf16) <- (-1x12x-1x-1xf16, -1x-1x-1x-1xf16)
        # shape: ([S0, 12, S1, S1]) <- ([S0, 12, S1, S1], [S0, 1, S1, S1])
        #  data: (None) <- (None, None)
        add_0 = reshape_0 + triu_0

        if FastReturn(3):
            return group_0, group_1, add_0

        #  type: (3xi64) <- (-1x-1x768xf16, -1x-1x64xf16)
        # shape: ([3]) <- ([S0, S1, 768], [S0*12, S1, 64])
        #  data: ([S0*12, S1, S1]) <- (None, None)
        generate_shape_1 = [(group_0.shape[0] * 12), group_1.shape[1], group_1.shape[1]] # inputs: group_0, group_1

        if FastReturn(4):
            return add_0, generate_shape_1

        #  type: (-1x-1x-1xf16, 0x-1x12x-1x-1xf16) <- (-1x12x-1x-1xf16, 3xi64)
        # shape: ([S0*12, S1, S1], [0, S0, 12, S1, S1]) <- ([S0, 12, S1, S1], [3])
        #  data: (None, None) <- (None, [S0*12, S1, S1])
        reshape_2, reshape_3 = paddle.reshape(add_0, generate_shape_1), None

        #  type: () <- (-1x-1x-1xf16)
        # shape: () <- ([S0*12, S1, S1])
        #  data: () <- (None)
        return reshape_2


class TestGroupOp(unittest.TestCase):
    def setUp(self):
        paddle.seed(2024)
        self.prepare_data()

    def prepare_data(self):
        self.inputs = [
            paddle.uniform([2, 2, 768], dtype='float16', min=-0.5, max=0.5),
            paddle.uniform([24, 2, 64], dtype='float16', min=-0.5, max=0.5),
            paddle.uniform([24, 2, 2], dtype='float16', min=-0.5, max=0.5),
            paddle.uniform([2, 1, 2, 2], dtype='float16', min=-0.5, max=0.5),
        ]
        for input in self.inputs:
          input.stop_gradient = True

    def apply_to_static(self, net, use_cinn):
        build_strategy = paddle.static.BuildStrategy()
        input_spec = [
            paddle.static.InputSpec(shape=[None, None, 768], dtype='float16'),
            paddle.static.InputSpec(shape=[None, None, 64], dtype='float16'),
            paddle.static.InputSpec(shape=[None, None, None], dtype='float16'),
            paddle.static.InputSpec(shape=[None, None, None, None], dtype='float16'),
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