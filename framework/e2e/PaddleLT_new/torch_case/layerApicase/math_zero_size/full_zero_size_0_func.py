import numpy as np
import torch
import torch.nn as nn


class LayerCase(nn.Module):
    """
    case名称: full_zero_size_func
    """

    def __init__(self):
        super(LayerCase, self).__init__()

    def forward(self, ):
        """
        forward
        """
        torch.manual_seed(33)
        np.random.seed(33)
        out = torch.full(size=[128, 0, 1], fill_value=3.0)
        return out


def create_tensor_inputs():
    """
    PyTorch tensor
    """
    inputs = ()
    return inputs


def create_numpy_inputs():
    """
    numpy array
    """
    inputs = ()
    return inputs
