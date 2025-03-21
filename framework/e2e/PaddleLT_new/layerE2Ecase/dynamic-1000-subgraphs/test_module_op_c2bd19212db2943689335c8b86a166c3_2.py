import os
os.environ['FLAGS_cinn_new_group_scheduler'] = '1'
os.environ['FLAGS_group_schedule_tiling_first'] = '1'
os.environ['FLAGS_enable_pir_api'] = '1'
os.environ['FLAGS_cinn_bucket_compile'] = '1'
import sys
import unittest
import numpy as np
from dataclasses import dataclass
import typing as t

@dataclass
class Stage:
    name: str
    env_vars: t.Dict[str, str]

cinn_stages = [
    Stage(
        name="dynamic_to_static",
        env_vars=dict(
            PADDLE_DEBUG_ENABLE_CINN=False,
            FLAGS_prim_all=False,
            FLAGS_prim_enable_dynamic=False,
        ),
    ),
    Stage(
        name="prim",
        env_vars=dict(
            PADDLE_DEBUG_ENABLE_CINN=False,
            FLAGS_prim_all=True,
            FLAGS_prim_enable_dynamic=True,
        ),
    ),
    Stage(
        name="infer_symbolic",
        env_vars=dict(
            PADDLE_DEBUG_ENABLE_CINN=False,
            FLAGS_prim_all=True,
            FLAGS_prim_enable_dynamic=True,
            FLAGS_use_cinn=False,
            FLAGS_check_infer_symbolic=True,
        ),
    ),
	Stage(
        name="frontend",
        env_vars=dict(
            PADDLE_DEBUG_ENABLE_CINN=True,
            FLAGS_prim_all=True,
            FLAGS_prim_enable_dynamic=True,
            FLAGS_use_cinn=True,
            FLAGS_check_infer_symbolic=False,
            FLAGS_enable_fusion_fallback=True,
        ), 
    ),
    Stage(
        name="backend",
        env_vars=dict(
            PADDLE_DEBUG_ENABLE_CINN=True,
            FLAGS_prim_all=True,
            FLAGS_prim_enable_dynamic=True,
            FLAGS_use_cinn=True,
            FLAGS_check_infer_symbolic=False,
            FLAGS_enable_fusion_fallback=False,
        ), 
    ),
]

def GetCinnStageByName(name):
    for stage in cinn_stages:
        if stage.name == name:
            return stage
    return None

def GetCurrentCinnStage():
    name = os.getenv('PADDLE_DEBUG_CINN_STAGE_NAME')
    if name is None:
        return None
    stage_names = [stage.name for stage in cinn_stages]
    assert name in stage_names, (
        f"PADDLE_DEBUG_CINN_STAGE_NAME should be in {stage_names}"
    )
    return GetCinnStageByName(name)

def GetPrevCinnStage(stage):
    for i in range(1, len(cinn_stages)):
        if stage is cinn_stages[i]:
            return cinn_stages[i - 1]
    return None

def IsCinnStageEnableDiff():
    value = os.getenv('PADDLE_DEBUG_CINN_STAGE_ENABLE_DIFF')
    enabled = value in {
        '1',
        'true',
        'True',
    }
    if enabled:
        assert GetCurrentCinnStage() is not None
    return enabled

def GetExitCodeAndStdErr(cmd, env):
    env = {
        k:v
        for k, v in env.items()
        if v is not None
    }
    import subprocess
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    return result.returncode, result.stderr

def GetStageExitCodeAndStdErr(stage):
    return GetExitCodeAndStdErr(
        [sys.executable, __file__],
        env=dict(
            PADDLE_DEBUG_CINN_STAGE_NAME=stage.name,
            PADDLE_DEBUG_CINN_STAGE_ENABLE_DIFF='0',
            PYTHONPATH=os.getenv('PYTHONPATH'),
            ATHENA_ENABLE_TRY_RUN="False",
        ),
    )

def AthenaTryRunEnabled():
    return os.getenv('ATHENA_ENABLE_TRY_RUN') not in {
        "0",
        "False",
        "false",
        "OFF"
    }

def GetNeedSkipAndSkipMessage():
    current_stage = GetCurrentCinnStage()
    assert current_stage is not None
    if not IsCinnStageEnableDiff():
        return False, ""
    last_stage = GetPrevCinnStage(current_stage)
    if last_stage is None:
        return False, ""
    exitcode, stderr = GetStageExitCodeAndStdErr(last_stage)
    if exitcode != 0:
        return True, f"last stage failed."
    return False, ""

def GetCurrentStageTryRunExitCodeAndStdErr():
    if not AthenaTryRunEnabled():
        return False, ""
    current_stage = GetCurrentCinnStage()
    assert current_stage is not None
    return GetStageExitCodeAndStdErr(current_stage)

def SetDefaultEnv(**env_var2value):
    for env_var, value in env_var2value.items():
        if os.getenv(env_var) is None:
            os.environ[env_var] = str(value)

SetDefaultEnv(
    PADDLE_DEBUG_CINN_STAGE_NAME="backend",
    PADDLE_DEBUG_CINN_STAGE_ENABLE_DIFF=False,
    PADDLE_DEBUG_ENABLE_CINN=True,
    FLAGS_enable_pir_api=True,
    FLAGS_prim_all=True,
    FLAGS_prim_enable_dynamic=True,
    FLAGS_use_cinn=False,
    FLAGS_check_infer_symbolic=False,
    FLAGS_enable_fusion_fallback=False,
)

need_skip, skip_message = GetNeedSkipAndSkipMessage()
try_run_exit_code, try_run_stderr = GetCurrentStageTryRunExitCodeAndStdErr()
class TestTryRun(unittest.TestCase):
    def test_panic(self):
        if not AthenaTryRunEnabled():
            return
        if try_run_exit_code == 0:
            # All unittest cases passed.
            return
        if try_run_exit_code > 0:
            # program failed but not panic.
            return
        # program panicked.
        kOutputLimit = 65536
        message = try_run_stderr[-kOutputLimit:]
        raise RuntimeError(f"panicked. last {kOutputLimit} characters of stderr: \n{message}")

import paddle

def SetEnvVar(env_var2value):
    for env_var, value in env_var2value.items():
        os.environ[env_var] = str(value)
    paddle.set_flags({
        env_var:value
        for env_var, value in env_var2value.items()
        if env_var.startswith('FLAGS_')
    })

if GetCurrentCinnStage() is not None:
    SetEnvVar(GetCurrentCinnStage().env_vars)

def NumOperationsInBlock(block_idx):
    return [44][block_idx] - 1 # number-of-ops-in-block

def GetPaddleDebugNumAllowedOps():
    try:
        return int(os.getenv('PADDLE_DEBUG_NUM_ALLOWED_OPS'))
    except:
        return None

paddle_debug_num_allowed_ops = GetPaddleDebugNumAllowedOps()


if type(paddle_debug_num_allowed_ops) is not int:
    def EarlyReturn(block_idx, op_idx):
        return False      
else:
    def EarlyReturn(block_idx, op_idx):
        return op_idx >= paddle_debug_num_allowed_ops

class BlockEntries:
    def builtin_module_251_0_0(self, parameter_6, parameter_7, parameter_9, parameter_1, parameter_3, parameter_2, parameter_11, parameter_8, parameter_4, parameter_10, parameter_5, parameter_0, data_0, data_1, data_2):

        # pd_op.layer_norm: (1x65536x32xf32, 1x65536xf32, 1x65536xf32) <- (1x65536x32xf32, 32xf32, 32xf32)
        layer_norm_0, layer_norm_1, layer_norm_2 = (lambda x, f: f(x))(paddle._C_ops.layer_norm(data_0, parameter_0, parameter_1, float('1e-06'), 2), lambda out: out if isinstance(out, (list, tuple)) else (out, None,None))

        # pd_op.matmul: (1x65536x32xf32) <- (1x65536x32xf32, 32x32xf32)
        matmul_0 = paddle.matmul(layer_norm_0, parameter_2, transpose_x=False, transpose_y=False)

        # pd_op.add: (1x65536x32xf32) <- (1x65536x32xf32, 32xf32)
        add_0 = matmul_0 + parameter_3

        # pd_op.full_int_array: (4xi64) <- ()
        full_int_array_0 = [1, 65536, 1, 32]

        # pd_op.reshape: (1x65536x1x32xf32, 0x1x65536x32xi64) <- (1x65536x32xf32, 4xi64)
        reshape_0, reshape_1 = (lambda x, f: f(x))(paddle._C_ops.reshape(add_0, full_int_array_0), lambda out: out if isinstance(out, (list, tuple)) else (out, None))

        # pd_op.transpose: (1x1x65536x32xf32) <- (1x65536x1x32xf32)
        transpose_0 = paddle._C_ops.transpose(reshape_0, [0, 2, 1, 3])

        # pd_op.transpose: (1x32x65536xf32) <- (1x65536x32xf32)
        transpose_1 = paddle._C_ops.transpose(layer_norm_0, [0, 2, 1])

        # pd_op.full: (xi64) <- ()
        full_0 = paddle._C_ops.full([], float('1'), paddle.int64, paddle.core.CPUPlace())

        # pd_op.full: (xi64) <- ()
        full_1 = paddle._C_ops.full([], float('32'), paddle.int64, paddle.core.CPUPlace())

        # pd_op.cast: (xi64) <- (xi32)
        cast_0 = paddle._C_ops.cast(data_1, paddle.int64)

        # pd_op.cast: (xi64) <- (xi32)
        cast_1 = paddle._C_ops.cast(data_2, paddle.int64)

        # builtin.combine: ([xi64, xi64, xi64, xi64]) <- (xi64, xi64, xi64, xi64)
        combine_0 = [full_0, full_1, cast_0, cast_1]

        # pd_op.stack: (4xi64) <- ([xi64, xi64, xi64, xi64])
        stack_0 = paddle._C_ops.stack(combine_0, 0)

        # pd_op.reshape: (1x32x-1x-1xf32, 0x1x32x65536xi64) <- (1x32x65536xf32, 4xi64)
        reshape_2, reshape_3 = (lambda x, f: f(x))(paddle._C_ops.reshape(transpose_1, stack_0), lambda out: out if isinstance(out, (list, tuple)) else (out, None))

        # pd_op.conv2d: (1x32x-1x-1xf32) <- (1x32x-1x-1xf32, 32x32x8x8xf32)
        conv2d_0 = paddle._C_ops.conv2d(reshape_2, parameter_4, [8, 8], [0, 0], 'EXPLICIT', [1, 1], 1, 'NCHW')

        # pd_op.full_int_array: (4xi64) <- ()
        full_int_array_1 = [1, -1, 1, 1]

        # pd_op.reshape: (1x32x1x1xf32, 0x32xi64) <- (32xf32, 4xi64)
        reshape_4, reshape_5 = (lambda x, f: f(x))(paddle._C_ops.reshape(parameter_5, full_int_array_1), lambda out: out if isinstance(out, (list, tuple)) else (out, None))

        # pd_op.add: (1x32x-1x-1xf32) <- (1x32x-1x-1xf32, 1x32x1x1xf32)
        add_1 = conv2d_0 + reshape_4

        # pd_op.full_int_array: (3xi64) <- ()
        full_int_array_2 = [1, 32, -1]

        # pd_op.reshape: (1x32x-1xf32, 0x1x32x-1x-1xi64) <- (1x32x-1x-1xf32, 3xi64)
        reshape_6, reshape_7 = (lambda x, f: f(x))(paddle._C_ops.reshape(add_1, full_int_array_2), lambda out: out if isinstance(out, (list, tuple)) else (out, None))

        # pd_op.transpose: (1x-1x32xf32) <- (1x32x-1xf32)
        transpose_2 = paddle._C_ops.transpose(reshape_6, [0, 2, 1])

        # pd_op.layer_norm: (1x-1x32xf32, 1x-1xf32, 1x-1xf32) <- (1x-1x32xf32, 32xf32, 32xf32)
        layer_norm_3, layer_norm_4, layer_norm_5 = (lambda x, f: f(x))(paddle._C_ops.layer_norm(transpose_2, parameter_6, parameter_7, float('1e-05'), 2), lambda out: out if isinstance(out, (list, tuple)) else (out, None,None))

        # pd_op.matmul: (1x-1x64xf32) <- (1x-1x32xf32, 32x64xf32)
        matmul_1 = paddle.matmul(layer_norm_3, parameter_8, transpose_x=False, transpose_y=False)

        # pd_op.add: (1x-1x64xf32) <- (1x-1x64xf32, 64xf32)
        add_2 = matmul_1 + parameter_9

        # pd_op.full_int_array: (5xi64) <- ()
        full_int_array_3 = [1, -1, 2, 1, 32]

        # pd_op.reshape: (1x-1x2x1x32xf32, 0x1x-1x64xi64) <- (1x-1x64xf32, 5xi64)
        reshape_8, reshape_9 = (lambda x, f: f(x))(paddle._C_ops.reshape(add_2, full_int_array_3), lambda out: out if isinstance(out, (list, tuple)) else (out, None))

        # pd_op.transpose: (2x1x1x-1x32xf32) <- (1x-1x2x1x32xf32)
        transpose_3 = paddle._C_ops.transpose(reshape_8, [2, 0, 3, 1, 4])

        # pd_op.full_int_array: (1xi64) <- ()
        full_int_array_4 = [0]

        # pd_op.full_int_array: (1xi64) <- ()
        full_int_array_5 = [1]

        # pd_op.assign: (1xi64) <- (1xi64)
        assign_0 = full_int_array_5

        # pd_op.slice: (1x1x-1x32xf32) <- (2x1x1x-1x32xf32, 1xi64, 1xi64)
        slice_0 = paddle._C_ops.slice(transpose_3, [0], full_int_array_4, full_int_array_5, [1], [0])

        # pd_op.full_int_array: (1xi64) <- ()
        full_int_array_6 = [2]

        # pd_op.slice: (1x1x-1x32xf32) <- (2x1x1x-1x32xf32, 1xi64, 1xi64)
        slice_1 = paddle._C_ops.slice(transpose_3, [0], assign_0, full_int_array_6, [1], [0])

        # pd_op.transpose: (1x1x32x-1xf32) <- (1x1x-1x32xf32)
        transpose_4 = paddle._C_ops.transpose(slice_0, [0, 1, 3, 2])

        # pd_op.matmul: (1x1x65536x-1xf32) <- (1x1x65536x32xf32, 1x1x32x-1xf32)
        matmul_2 = paddle.matmul(transpose_0, transpose_4, transpose_x=False, transpose_y=False)

        # pd_op.full: (1xf32) <- ()
        full_2 = paddle._C_ops.full([1], float('0.176777'), paddle.float32, paddle.core.CPUPlace())

        # pd_op.scale: (1x1x65536x-1xf32) <- (1x1x65536x-1xf32, 1xf32)
        scale_0 = paddle._C_ops.scale(matmul_2, full_2, float('0'), True)

        # pd_op.softmax: (1x1x65536x-1xf32) <- (1x1x65536x-1xf32)
        softmax_0 = paddle._C_ops.softmax(scale_0, -1)

        # pd_op.matmul: (1x1x65536x32xf32) <- (1x1x65536x-1xf32, 1x1x-1x32xf32)
        matmul_3 = paddle.matmul(softmax_0, slice_1, transpose_x=False, transpose_y=False)

        # pd_op.transpose: (1x65536x1x32xf32) <- (1x1x65536x32xf32)
        transpose_5 = paddle._C_ops.transpose(matmul_3, [0, 2, 1, 3])

        # pd_op.full_int_array: (3xi64) <- ()
        full_int_array_7 = [1, 65536, 32]

        # pd_op.reshape: (1x65536x32xf32, 0x1x65536x1x32xi64) <- (1x65536x1x32xf32, 3xi64)
        reshape_10, reshape_11 = (lambda x, f: f(x))(paddle._C_ops.reshape(transpose_5, full_int_array_7), lambda out: out if isinstance(out, (list, tuple)) else (out, None))

        # pd_op.matmul: (1x65536x32xf32) <- (1x65536x32xf32, 32x32xf32)
        matmul_4 = paddle.matmul(reshape_10, parameter_10, transpose_x=False, transpose_y=False)

        # pd_op.add: (1x65536x32xf32) <- (1x65536x32xf32, 32xf32)
        add_3 = matmul_4 + parameter_11
        return layer_norm_0, layer_norm_1, layer_norm_2, matmul_0, reshape_1, transpose_0, reshape_2, reshape_3, conv2d_0, reshape_4, reshape_5, reshape_7, transpose_2, layer_norm_3, layer_norm_4, layer_norm_5, matmul_1, reshape_9, transpose_3, full_int_array_4, full_int_array_5, assign_0, full_int_array_6, slice_1, transpose_4, full_2, softmax_0, reshape_10, reshape_11, matmul_4, add_3



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


class CinnTestBase:
    def setUp(self):
        paddle.seed(2024)
        self.prepare_data()

    def _test_entry(self):
        dy_outs = self.entry(use_cinn=False)
        cinn_outs = self.entry(use_cinn=GetEnvVarEnableCinn())

        for cinn_out, dy_out in zip(cinn_outs, dy_outs):
          if type(cinn_out) is list and type(dy_out) is list:
            for x, y in zip(cinn_out, dy_out):
              self.assert_all_close(x, y)
          else:
            self.assert_all_close(cinn_out, dy_out)

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

class ModuleOp(paddle.nn.Layer, BlockEntries):
    def __init__(self):
        super().__init__()

    def forward(self, parameter_6, parameter_7, parameter_9, parameter_1, parameter_3, parameter_2, parameter_11, parameter_8, parameter_4, parameter_10, parameter_5, parameter_0, data_0, data_1, data_2):
        return self.builtin_module_251_0_0(parameter_6, parameter_7, parameter_9, parameter_1, parameter_3, parameter_2, parameter_11, parameter_8, parameter_4, parameter_10, parameter_5, parameter_0, data_0, data_1, data_2)

@unittest.skipIf(need_skip, skip_message)
class Test_builtin_module_251_0_0(CinnTestBase, unittest.TestCase):
    def prepare_data(self):
        self.inputs = [
            # parameter_6
            paddle.uniform([32], dtype='float32', min=0, max=0.5),
            # parameter_7
            paddle.uniform([32], dtype='float32', min=0, max=0.5),
            # parameter_9
            paddle.uniform([64], dtype='float32', min=0, max=0.5),
            # parameter_1
            paddle.uniform([32], dtype='float32', min=0, max=0.5),
            # parameter_3
            paddle.uniform([32], dtype='float32', min=0, max=0.5),
            # parameter_2
            paddle.uniform([32, 32], dtype='float32', min=0, max=0.5),
            # parameter_11
            paddle.uniform([32], dtype='float32', min=0, max=0.5),
            # parameter_8
            paddle.uniform([32, 64], dtype='float32', min=0, max=0.5),
            # parameter_4
            paddle.uniform([32, 32, 8, 8], dtype='float32', min=0, max=0.5),
            # parameter_10
            paddle.uniform([32, 32], dtype='float32', min=0, max=0.5),
            # parameter_5
            paddle.uniform([32], dtype='float32', min=0, max=0.5),
            # parameter_0
            paddle.uniform([32], dtype='float32', min=0, max=0.5),
            # data_0
            paddle.uniform([1, 65536, 32], dtype='float32', min=0, max=0.5),
            # data_1
            paddle.to_tensor([128], dtype='int32').reshape([]),
            # data_2
            paddle.to_tensor([512], dtype='int32').reshape([]),
        ]
        for input in self.inputs:
            input.stop_gradient = True

    def apply_to_static(self, net, use_cinn):
        build_strategy = paddle.static.BuildStrategy()
        input_spec = [
            # parameter_6
            paddle.static.InputSpec(shape=[32], dtype='float32'),
            # parameter_7
            paddle.static.InputSpec(shape=[32], dtype='float32'),
            # parameter_9
            paddle.static.InputSpec(shape=[64], dtype='float32'),
            # parameter_1
            paddle.static.InputSpec(shape=[32], dtype='float32'),
            # parameter_3
            paddle.static.InputSpec(shape=[32], dtype='float32'),
            # parameter_2
            paddle.static.InputSpec(shape=[32, 32], dtype='float32'),
            # parameter_11
            paddle.static.InputSpec(shape=[32], dtype='float32'),
            # parameter_8
            paddle.static.InputSpec(shape=[32, 64], dtype='float32'),
            # parameter_4
            paddle.static.InputSpec(shape=[32, 32, 8, 8], dtype='float32'),
            # parameter_10
            paddle.static.InputSpec(shape=[32, 32], dtype='float32'),
            # parameter_5
            paddle.static.InputSpec(shape=[32], dtype='float32'),
            # parameter_0
            paddle.static.InputSpec(shape=[32], dtype='float32'),
            # data_0
            paddle.static.InputSpec(shape=[1, 65536, 32], dtype='float32'),
            # data_1
            paddle.static.InputSpec(shape=[], dtype='int32'),
            # data_2
            paddle.static.InputSpec(shape=[], dtype='int32'),
        ]
        build_strategy.build_cinn_pass = use_cinn
        return paddle.jit.to_static(
            net,
            input_spec=input_spec,
            build_strategy=build_strategy,
            full_graph=True,
        )

    def entry(self, use_cinn):
        net = ModuleOp()
        if GetEnvVarEnableJit():
            net = self.apply_to_static(net, use_cinn)
        paddle.seed(2024)
        out = net(*self.inputs)
        return out

    def test_entry(self):
        if AthenaTryRunEnabled():
            if try_run_exit_code == 0:
                # All unittest cases passed.
                return
            if try_run_exit_code < 0:
                # program panicked.
                raise RuntimeError(f"panicked. panic stderr have been reported by the unittest `TestTryRun.test_panic`.")
        self._test_entry()

if __name__ == '__main__':
    unittest.main()