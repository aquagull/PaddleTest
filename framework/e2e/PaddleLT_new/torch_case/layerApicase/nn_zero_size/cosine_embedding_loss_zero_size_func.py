import numpy as np
import torch
import torch.nn as nn


class LayerCase(nn.Module):
    """
    case名称: cosine_embedding_loss_zero_size_class
    """

    def __init__(self):
        super(LayerCase, self).__init__()

    def forward(self, x, y, label):
        """
        forward
        """
        torch.manual_seed(33)
        np.random.seed(33)
        out = nn.functional.cosine_embedding_loss(
            x, y, label,
            margin=0,
            reduction='mean',
        )
        return out


def create_tensor_inputs():
    """
    PyTorch tensor
    """
    inputs = (
        torch.tensor((-1 + 2 * np.random.random([10, 0])).astype(np.float32), dtype=torch.float32, requires_grad=True), 
        torch.tensor((-1 + 2 * np.random.random([10, 0])).astype(np.float32), dtype=torch.float32, requires_grad=True), 
        torch.tensor((-1 + 2 * np.random.random([10])).astype(np.float32), dtype=torch.float32, requires_grad=True), 
    )
    return inputs


def create_numpy_inputs():
    """
    numpy array
    """
    inputs = (
        (-1 + 2 * np.random.random([10, 0])).astype('float32'),
        (-1 + 2 * np.random.random([10, 0])).astype('float32'),
        (-1 + 2 * np.random.random([10])).astype('float32'),
    )
    return inputs
