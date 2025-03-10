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
        return True
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



class PrimitiveOp_c5cbc90fe6159106c92d9b8ef618ab57(InstanceTrait, paddle.nn.Layer):
    
    def __init__(self):
        super().__init__()

    def forward(self, input_0, input_1):
        return paddle.gather_nd(input_0, input_1)

    def get_input_spec(self):
        return [
            paddle.static.InputSpec(shape=[4, 80, 28, 28], dtype='float32'),
            paddle.static.InputSpec(shape=[3136, 4], dtype='int64'),
        ]
        
    instance_ = None
    static_instance_with_cinn_ = None
    static_instance_without_cinn_ = None


class TestPrimitiveOp_e43f25420532151b5b297d35609da8fc(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_c5cbc90fe6159106c92d9b8ef618ab57
    def get_inputs(self):
        return [
            paddle.uniform([4, 80, 28, 28], dtype='float32', min=0, max=0.5),
            paddle.randint(low=0, high=3, shape=[3136, 4], dtype='int64'),
        ]


class PrimitiveOp_8793d3c14f89f50947d77704ecee325a(InstanceTrait, paddle.nn.Layer):
    
    def __init__(self):
        super().__init__()

    def forward(self, input_0, input_1):
        return paddle.gather_nd(input_0, input_1)

    def get_input_spec(self):
        return [
            paddle.static.InputSpec(shape=[1, 41344, 128], dtype='float32'),
            paddle.static.InputSpec(shape=[1, 500, 2], dtype='int64'),
        ]
        
    instance_ = None
    static_instance_with_cinn_ = None
    static_instance_without_cinn_ = None


class TestPrimitiveOp_2037c82c91c83b9cc3bf90d0274647cf(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_8793d3c14f89f50947d77704ecee325a
    def get_inputs(self):
        return [
            paddle.uniform([1, 41344, 128], dtype='float32', min=0, max=0.5),
            paddle.randint(low=0, high=3, shape=[1, 500, 2], dtype='int64'),
        ]


class PrimitiveOp_a3e224feab9b9588615e215905e685d5(InstanceTrait, paddle.nn.Layer):
    
    def __init__(self):
        super().__init__()

    def forward(self, input_0, input_1):
        return paddle.gather_nd(input_0, input_1)

    def get_input_spec(self):
        return [
            paddle.static.InputSpec(shape=[1, 25920, 128], dtype='float32'),
            paddle.static.InputSpec(shape=[1, 500, 2], dtype='int64'),
        ]
        
    instance_ = None
    static_instance_with_cinn_ = None
    static_instance_without_cinn_ = None


class TestPrimitiveOp_0ebf330143d5a8ca75177804b8dc97b2(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_a3e224feab9b9588615e215905e685d5
    def get_inputs(self):
        return [
            paddle.uniform([1, 25920, 128], dtype='float32', min=0, max=0.5),
            paddle.randint(low=0, high=3, shape=[1, 500, 2], dtype='int64'),
        ]


class PrimitiveOp_3fe878ddfa093b587a550588f5a26119(InstanceTrait, paddle.nn.Layer):
    
    def __init__(self):
        super().__init__()

    def forward(self, input_0, input_1):
        return paddle.gather_nd(input_0, input_1)

    def get_input_spec(self):
        return [
            paddle.static.InputSpec(shape=[3, 80, 28, 28], dtype='float32'),
            paddle.static.InputSpec(shape=[2352, 4], dtype='int64'),
        ]
        
    instance_ = None
    static_instance_with_cinn_ = None
    static_instance_without_cinn_ = None


class TestPrimitiveOp_b0c8afcc851cbc1a623d2601c8105fc4(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_3fe878ddfa093b587a550588f5a26119
    def get_inputs(self):
        return [
            paddle.uniform([3, 80, 28, 28], dtype='float32', min=0, max=0.5),
            paddle.randint(low=0, high=3, shape=[2352, 4], dtype='int64'),
        ]


class PrimitiveOp_b4e4089cc4311356212d3d47e0729057(InstanceTrait, paddle.nn.Layer):
    
    def __init__(self):
        super().__init__()

    def forward(self, input_0, input_1):
        return paddle.gather_nd(input_0, input_1)

    def get_input_spec(self):
        return [
            paddle.static.InputSpec(shape=[6, 80, 28, 28], dtype='float32'),
            paddle.static.InputSpec(shape=[4704, 4], dtype='int64'),
        ]
        
    instance_ = None
    static_instance_with_cinn_ = None
    static_instance_without_cinn_ = None


class TestPrimitiveOp_bcdc6a19aaaf7d79b1e2c7010986c885(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_b4e4089cc4311356212d3d47e0729057
    def get_inputs(self):
        return [
            paddle.uniform([6, 80, 28, 28], dtype='float32', min=0, max=0.5),
            paddle.randint(low=0, high=3, shape=[4704, 4], dtype='int64'),
        ]


class PrimitiveOp_286ec234efa823d4fff4892256853837(InstanceTrait, paddle.nn.Layer):
    
    def __init__(self):
        super().__init__()

    def forward(self, input_0, input_1):
        return paddle.gather_nd(input_0, input_1)

    def get_input_spec(self):
        return [
            paddle.static.InputSpec(shape=[2, 80, 28, 28], dtype='float32'),
            paddle.static.InputSpec(shape=[1568, 4], dtype='int64'),
        ]
        
    instance_ = None
    static_instance_with_cinn_ = None
    static_instance_without_cinn_ = None


class TestPrimitiveOp_2bfeead678422925276ec1183886bb5f(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_286ec234efa823d4fff4892256853837
    def get_inputs(self):
        return [
            paddle.uniform([2, 80, 28, 28], dtype='float32', min=0, max=0.5),
            paddle.randint(low=0, high=3, shape=[1568, 4], dtype='int64'),
        ]


class PrimitiveOp_c3fecdd212fa79ad20db264e06a0d557(InstanceTrait, paddle.nn.Layer):
    
    def __init__(self):
        super().__init__()

    def forward(self, input_0, input_1):
        return paddle.gather_nd(input_0, input_1)

    def get_input_spec(self):
        return [
            paddle.static.InputSpec(shape=[1, 11520, 128], dtype='float32'),
            paddle.static.InputSpec(shape=[1, 500, 2], dtype='int64'),
        ]
        
    instance_ = None
    static_instance_with_cinn_ = None
    static_instance_without_cinn_ = None


class TestPrimitiveOp_c1a0c9443575271df30f957b1d4c4de8(CinnTestBase, unittest.TestCase):
    
    def get_test_class(self):
        return PrimitiveOp_c3fecdd212fa79ad20db264e06a0d557
    def get_inputs(self):
        return [
            paddle.uniform([1, 11520, 128], dtype='float32', min=0, max=0.5),
            paddle.randint(low=0, high=3, shape=[1, 500, 2], dtype='int64'),
        ]




if __name__ == '__main__':
    unittest.main()