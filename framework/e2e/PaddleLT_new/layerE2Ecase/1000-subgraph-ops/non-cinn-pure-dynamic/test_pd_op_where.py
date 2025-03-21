import os
if os.getenv('FLAGS_cinn_new_group_scheduler') is None:
    os.environ['FLAGS_cinn_new_group_scheduler'] = '1'
if os.getenv('FLAGS_group_schedule_tiling_first') is None:
    os.environ['FLAGS_group_schedule_tiling_first'] = '1'
if os.getenv('FLAGS_prim_all') is None:
    os.environ['FLAGS_prim_all'] = 'true'
if os.getenv('FLAGS_prim_enable_dynamic') is None:
    os.environ['FLAGS_prim_enable_dynamic'] = '1'
if os.getenv('FLAGS_enable_pir_api') is None:
    os.environ['FLAGS_enable_pir_api'] = '1'
if os.getenv('FLAGS_cinn_bucket_compile') is None:
    os.environ['FLAGS_cinn_bucket_compile'] = '1'

import unittest
import numpy as np
import paddle

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
    if enable_cinn is None:
        return False
    return enable_cinn not in {
        "0",
        "False",
        "false",
        "OFF",
    }


def GetTolerance(dtype):
    if dtype == np.float16:
        return GetFloat16Tolerance()
    if dtype == np.float32:
        return GetFloat32Tolerance()
    return 1e-6

def GetFloat16Tolerance():
    try:
        return float(os.getenv('PADDLE_DEBUG_FLOAT16_TOL'))
    except:
        return 1e-3

def GetFloat32Tolerance():
    try:
        return float(os.getenv('PADDLE_DEBUG_FLOAT32_TOL'))
    except:
        return 1e-6

def IsInteger(dtype):
    return np.dtype(dtype).char in np.typecodes['AllInteger']

def ApplyToStatic(net, use_cinn):
    build_strategy = paddle.static.BuildStrategy()
    build_strategy.build_cinn_pass = use_cinn
    return paddle.jit.to_static(
        net,
        input_spec=net.get_input_spec(),
        build_strategy=build_strategy,
        full_graph=True,
    )

class InstanceTrait:

    @classmethod
    def instance(cls):
        if cls.instance_ is None:
            cls.instance_ = cls()
        return cls.instance_

    @classmethod
    def static_instance_with_cinn(cls):
        if cls.static_instance_with_cinn_ is None:
            cls.static_instance_with_cinn_ = ApplyToStatic(
                cls.instance(),
                use_cinn=True
            )
        return cls.static_instance_with_cinn_

    @classmethod
    def static_instance_without_cinn(cls):
        if cls.static_instance_without_cinn_ is None:
            cls.static_instance_without_cinn_ = ApplyToStatic(
                cls.instance(),
                use_cinn=False
            )
        return cls.static_instance_without_cinn_


class CinnTestBase:

    def setUp(self):
        paddle.seed(2024)
        self.prepare_data()

    def test_train(self):
        dy_outs = self.train(use_cinn=False)
        cinn_outs = self.train(use_cinn=GetEnvVarEnableCinn())

        for cinn_out, dy_out in zip(cinn_outs, dy_outs):
          if type(cinn_out) is list and type(dy_out) is list:
            for x, y in zip(cinn_out, dy_out):
              self.assert_all_close(x, y)
          else:
            self.assert_all_close(cinn_out, dy_out)

    def train(self, use_cinn):
        if GetEnvVarEnableJit():
            net = self.prepare_static_net(use_cinn)
        else:
            net = self.prepare_net()
        out = net(*self.inputs)
        return out
    
    def prepare_data(self):
        self.inputs = self.get_inputs()
        for input in self.inputs:
            input.stop_gradient = True

    def prepare_net(self):
        return self.get_test_class().instance()

    def prepare_static_net(self, use_cinn):
        if use_cinn:
            return self.get_test_class().static_instance_with_cinn()
        else:
            return self.get_test_class().static_instance_without_cinn()

    def assert_all_close(self, x, y):
        if (hasattr(x, "numpy") and hasattr(y, "numpy")):
            x_numpy = x.numpy()
            y_numpy = y.numpy()
            assert x_numpy.dtype == y_numpy.dtype
            if IsInteger(x_numpy.dtype):
                np.testing.assert_equal(x_numpy, y_numpy)
            else:
                tol = GetTolerance(x_numpy.dtype)
                np.testing.assert_allclose(x_numpy, y_numpy, atol=tol, rtol=tol)
        else:
            assert x == y



class PrimitiveOp_a909bbc32f077ec2d4127bd257fc270a(InstanceTrait, paddle.nn.Layer):
    
    def __init__(self):
        super().__init__()

    def forward(self, input_0, input_1, input_2):
        return paddle._C_ops.where(input_0, input_1, input_2)

    def get_input_spec(self):
        return [
            paddle.static.InputSpec(shape=[None, None], dtype='bool'),
            paddle.static.InputSpec(shape=[None, None], dtype='float32'),
            paddle.static.InputSpec(shape=[None, None], dtype='float32'),
        ]
        
    instance_ = None
    static_instance_with_cinn_ = None
    static_instance_without_cinn_ = None


class TestPrimitiveOp_209b72c0df784fe5d873fafa8a45c959(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_a909bbc32f077ec2d4127bd257fc270a
    def get_inputs(self):
        return [
            paddle.cast(paddle.randint(low=0, high=2, shape=[1024, 5], dtype='int32'), 'bool'),
            paddle.uniform([1024, 5], dtype='float32', min=0, max=0.5),
            paddle.uniform([1024, 5], dtype='float32', min=0, max=0.5),
        ]


class PrimitiveOp_82afe4610964ac5afb1051ec4c99577b(InstanceTrait, paddle.nn.Layer):
    
    def __init__(self):
        super().__init__()

    def forward(self, input_0, input_1, input_2):
        return paddle._C_ops.where(input_0, input_1, input_2)

    def get_input_spec(self):
        return [
            paddle.static.InputSpec(shape=[None, None], dtype='bool'),
            paddle.static.InputSpec(shape=[None, None], dtype='int32'),
            paddle.static.InputSpec(shape=[None, None], dtype='int32'),
        ]
        
    instance_ = None
    static_instance_with_cinn_ = None
    static_instance_without_cinn_ = None


class TestPrimitiveOp_1899462f4751eb762ba8c5f83315f42b(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_82afe4610964ac5afb1051ec4c99577b
    def get_inputs(self):
        return [
            paddle.cast(paddle.randint(low=0, high=2, shape=[1, 2100], dtype='int32'), 'bool'),
            paddle.randint(low=0, high=3, shape=[1, 2100], dtype='int32'),
            paddle.randint(low=0, high=3, shape=[1, 2100], dtype='int32'),
        ]


class TestPrimitiveOp_749a5d41aaae9fae13e9da2a8f421b4e(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_a909bbc32f077ec2d4127bd257fc270a
    def get_inputs(self):
        return [
            paddle.cast(paddle.randint(low=0, high=2, shape=[4096, 5], dtype='int32'), 'bool'),
            paddle.uniform([4096, 5], dtype='float32', min=0, max=0.5),
            paddle.uniform([4096, 5], dtype='float32', min=0, max=0.5),
        ]


class PrimitiveOp_7cce25297d24a719c0e0f4e4483876b6(InstanceTrait, paddle.nn.Layer):
    
    def __init__(self):
        super().__init__()

    def forward(self, input_0, input_1, input_2):
        return paddle._C_ops.where(input_0, input_1, input_2)

    def get_input_spec(self):
        return [
            paddle.static.InputSpec(shape=[None], dtype='bool'),
            paddle.static.InputSpec(shape=[None], dtype='int32'),
            paddle.static.InputSpec(shape=[None], dtype='int32'),
        ]
        
    instance_ = None
    static_instance_with_cinn_ = None
    static_instance_without_cinn_ = None


class TestPrimitiveOp_16040f3de79e584b1b029e755f834f55(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_7cce25297d24a719c0e0f4e4483876b6
    def get_inputs(self):
        return [
            paddle.cast(paddle.randint(low=0, high=2, shape=[2002], dtype='int32'), 'bool'),
            paddle.randint(low=0, high=3, shape=[2002], dtype='int32'),
            paddle.randint(low=0, high=3, shape=[2002], dtype='int32'),
        ]


class TestPrimitiveOp_16040f3de79e584b1b029e755f834f55(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_7cce25297d24a719c0e0f4e4483876b6
    def get_inputs(self):
        return [
            paddle.cast(paddle.randint(low=0, high=2, shape=[2002], dtype='int32'), 'bool'),
            paddle.randint(low=0, high=3, shape=[2002], dtype='int32'),
            paddle.randint(low=0, high=3, shape=[2002], dtype='int32'),
        ]


class TestPrimitiveOp_4599c7e97546ae678773112a2f7cbb37(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_7cce25297d24a719c0e0f4e4483876b6
    def get_inputs(self):
        return [
            paddle.cast(paddle.randint(low=0, high=2, shape=[1021], dtype='int32'), 'bool'),
            paddle.randint(low=0, high=3, shape=[1021], dtype='int32'),
            paddle.randint(low=0, high=3, shape=[1021], dtype='int32'),
        ]


class TestPrimitiveOp_4599c7e97546ae678773112a2f7cbb37(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_7cce25297d24a719c0e0f4e4483876b6
    def get_inputs(self):
        return [
            paddle.cast(paddle.randint(low=0, high=2, shape=[1021], dtype='int32'), 'bool'),
            paddle.randint(low=0, high=3, shape=[1021], dtype='int32'),
            paddle.randint(low=0, high=3, shape=[1021], dtype='int32'),
        ]


class TestPrimitiveOp_66f2d6444b7f056b74e3da39d707da88(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_7cce25297d24a719c0e0f4e4483876b6
    def get_inputs(self):
        return [
            paddle.cast(paddle.randint(low=0, high=2, shape=[1002], dtype='int32'), 'bool'),
            paddle.randint(low=0, high=3, shape=[1002], dtype='int32'),
            paddle.randint(low=0, high=3, shape=[1002], dtype='int32'),
        ]


class TestPrimitiveOp_66f2d6444b7f056b74e3da39d707da88(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_7cce25297d24a719c0e0f4e4483876b6
    def get_inputs(self):
        return [
            paddle.cast(paddle.randint(low=0, high=2, shape=[1002], dtype='int32'), 'bool'),
            paddle.randint(low=0, high=3, shape=[1002], dtype='int32'),
            paddle.randint(low=0, high=3, shape=[1002], dtype='int32'),
        ]


class TestPrimitiveOp_9aa5dbb2cd82e8d0798f1b75ffa4869d(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_a909bbc32f077ec2d4127bd257fc270a
    def get_inputs(self):
        return [
            paddle.cast(paddle.randint(low=0, high=2, shape=[64, 5], dtype='int32'), 'bool'),
            paddle.uniform([64, 5], dtype='float32', min=0, max=0.5),
            paddle.uniform([64, 5], dtype='float32', min=0, max=0.5),
        ]


class TestPrimitiveOp_0bf398367d2c9e07eef727dd056b2eba(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_82afe4610964ac5afb1051ec4c99577b
    def get_inputs(self):
        return [
            paddle.cast(paddle.randint(low=0, high=2, shape=[1, 3549], dtype='int32'), 'bool'),
            paddle.randint(low=0, high=3, shape=[1, 3549], dtype='int32'),
            paddle.randint(low=0, high=3, shape=[1, 3549], dtype='int32'),
        ]


class TestPrimitiveOp_7c6c559582901e639d4c092e2b0b40f5(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_82afe4610964ac5afb1051ec4c99577b
    def get_inputs(self):
        return [
            paddle.cast(paddle.randint(low=0, high=2, shape=[1, 4116], dtype='int32'), 'bool'),
            paddle.randint(low=0, high=3, shape=[1, 4116], dtype='int32'),
            paddle.randint(low=0, high=3, shape=[1, 4116], dtype='int32'),
        ]


class TestPrimitiveOp_1fc5f816ae883515530727664f1f4272(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_a909bbc32f077ec2d4127bd257fc270a
    def get_inputs(self):
        return [
            paddle.cast(paddle.randint(low=0, high=2, shape=[16384, 5], dtype='int32'), 'bool'),
            paddle.uniform([16384, 5], dtype='float32', min=0, max=0.5),
            paddle.uniform([16384, 5], dtype='float32', min=0, max=0.5),
        ]


class TestPrimitiveOp_fa41b75c5b007cd8225ecb875fe1014f(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_7cce25297d24a719c0e0f4e4483876b6
    def get_inputs(self):
        return [
            paddle.cast(paddle.randint(low=0, high=2, shape=[1027], dtype='int32'), 'bool'),
            paddle.randint(low=0, high=3, shape=[1027], dtype='int32'),
            paddle.randint(low=0, high=3, shape=[1027], dtype='int32'),
        ]


class TestPrimitiveOp_fa41b75c5b007cd8225ecb875fe1014f(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_7cce25297d24a719c0e0f4e4483876b6
    def get_inputs(self):
        return [
            paddle.cast(paddle.randint(low=0, high=2, shape=[1027], dtype='int32'), 'bool'),
            paddle.randint(low=0, high=3, shape=[1027], dtype='int32'),
            paddle.randint(low=0, high=3, shape=[1027], dtype='int32'),
        ]


class TestPrimitiveOp_6eb596e8c522adf431ef575da1a83fc3(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_a909bbc32f077ec2d4127bd257fc270a
    def get_inputs(self):
        return [
            paddle.cast(paddle.randint(low=0, high=2, shape=[256, 5], dtype='int32'), 'bool'),
            paddle.uniform([256, 5], dtype='float32', min=0, max=0.5),
            paddle.uniform([256, 5], dtype='float32', min=0, max=0.5),
        ]




if __name__ == '__main__':
    unittest.main()