import torch
import time
import torch.nn.functional as F
from torch_geometric.nn import MessagePassing
from torch.nn import Parameter
import matplotlib.pyplot as plt
import torch.nn as nn

class CustomGraphConv(nn.Module):
    def __init__(self,in_channels, out_channels, GNNData):
        super().__init__()
        self.pointCenter = GNNCenterPointCenterSimple(GNNData, in_channels, out_channels)

    def forward(self, x, edge_index, edge_attr,graphData):
        x = self.pointCenter(x, edge_index, edge_attr,graphData)
        return x


class CustomGraphConvPointPoint(nn.Module):
    def __init__(self,in_channels, out_channels, GNNData):
        super().__init__()
        self.pointPoint = GNNpointPoint(GNNData, in_channels, out_channels)

    def forward(self, x, edge_index, edge_attr):
        x = self.pointPoint(x, edge_index, edge_attr)
        return x


class GNNpointPoint(MessagePassing):
    def __init__(self, GNNData, in_channels, out_channels):
        super().__init__(aggr='add')
        self.weight_matrix = torch.nn.Parameter(torch.Tensor(GNNData["nEdgeAttr"], out_channels, in_channels))
        self.bias = Parameter(torch.empty(out_channels))
        self.reset_parameters(in_channels, out_channels)

    def reset_parameters(self,in_channels, out_channels):
        # scale_factor = torch.sqrt(torch.tensor(2.0 / (in_channels+out_channels)))
        #
        # with torch.no_grad():
        #     # self.weight_matrix.uniform_(-scale_factor, scale_factor)
        #     self.weight_matrix.uniform_(-scale_factor, scale_factor)
        torch.nn.init.ones_(self.weight_matrix)
        torch.nn.init.zeros_(self.bias)

    def forward(self, x, edge_index, edge_attr):
        conv_result = self.propagate(edge_index, x=x, edge_attr=edge_attr)
        return conv_result

    def message(self, x_j, edge_attr):
        x_j = x_j.unsqueeze(-1)

        weights_matrices = torch.einsum('ij,jkl->ikl', edge_attr, self.weight_matrix)

        results = torch.matmul(weights_matrices, x_j).squeeze(-1)
        return results

    def update(self, aggr_out):
        return F.relu(aggr_out + self.bias)

class GNNCenterPointCenterSimple(MessagePassing):
    def __init__(self, GNNData, in_channels, out_channels):
        super().__init__(aggr='add')
        self.weight_matrix = torch.nn.Parameter(torch.Tensor(GNNData["nEdgeAttr"], out_channels, in_channels))
        self.bias = Parameter(torch.empty(out_channels))
        self.reset_parameters(in_channels, out_channels)

    def reset_parameters(self,in_channels, out_channels):
        # scale_factor = torch.sqrt(torch.tensor(2.0 / (in_channels+out_channels)))
        #
        # with torch.no_grad():
        #     # self.weight_matrix.uniform_(-scale_factor, scale_factor)
        #     self.weight_matrix.uniform_(-scale_factor, scale_factor)

        torch.nn.init.ones_(self.weight_matrix)

        torch.nn.init.zeros_(self.bias)

    def forward(self, x, edge_index, edge_attr, graphData):


        conv_result = self.propagate(edge_index, x=x, edge_attr=edge_attr, size=(graphData["inputSize"], graphData["outputSize"]))
        # conv_result = self.propagate(edge_index, x=x, edge_attr=edge_attr, size=(graphData["inputSize"], graphData["inputSize"]))

        return conv_result

    def message(self, x_j, edge_attr):
        x_j = x_j.unsqueeze(-1)

        weights_matrices = torch.einsum('ij,jkl->ikl', edge_attr, self.weight_matrix)

        results = torch.matmul(weights_matrices, x_j).squeeze(-1)
        return results

    def update(self, aggr_out):
        return F.relu(aggr_out + self.bias)

# class SelfLoopLayer(MessagePassing):
#     def __init__(self, in_channels, out_channels):
#         super(SelfLoopLayer, self).__init__(aggr='add')
#         self.lin = torch.nn.Linear(in_channels, out_channels)
#
#     def forward(self, x):
#         x_result = self.lin(x)
#         return x_result
class SelfLoopLayer(MessagePassing):
    def __init__(self):
        super(SelfLoopLayer, self).__init__(aggr='add')
        # Removed the linear layer since it's not needed

    def forward(self, x):
        # Sum along the last dimension (c), keeping the second dimension (b) intact
        x_result = torch.sum(x, dim=-1, keepdim=True)  # Summing along the last dimension and keeping dimension
        return x_result
