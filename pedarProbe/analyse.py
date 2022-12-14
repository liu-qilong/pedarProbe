"""Data analysis functionalities. Short-cut functions are realised in :class:`pedarProbe.node.PedarNode` to facilitate the usability.
"""
from __future__ import annotations
from typing import Type, Union

import pandas as pd

import node as pedarnode

def sensor_peak(node: pedarnode.DataNode) -> pd.core.series.Series:
    """Compute the peak pressure of each sensor.
    
    Parameters
    ---
    node
        the :class:`pedarProbe.node.DataNode` object.

    Return
    ---
    :class:`pandas.core.series.Series`
        the peak pressure of each sensor, with sensor ID as the index.
    """
    return node.df.max()


def sensor_pti(node: pedarnode.DataNode) -> pd.core.series.Series:
    """Compute the pressure-time integral (PTI) of each sensor.
    
    Parameters
    ---
    node
        the :class:`pedarProbe.node.DataNode` object.

    Return
    ---
    :class:`pandas.core.series.Series`
        the peak pressure of each sensor, with sensor ID as the index.
    """
    time_unit = node.df.index[1] - node.df.index[0]
    pt = node.df * time_unit
    pti = pt.sum()
    return pti


def attribute_average_up(node: Type[pedarnode.PedarNode], attr_name: str = 'sensor_peak', attr_func: function = sensor_peak):
    """Recursively compute the attribute for each leaf node and then average it up as the upper node's attribute layer by layer, towards root node level. The added attribute will be added to :class:`~pedarProbe.node.PedarNode`'s :attr:`attributes` dictionary.

    Parameters
    ---
    node
        root node of the node tree.
    attr_name
        attribute name. Also as the keyword of the added item to :attr:`self.attributes` dictionary.
    attr_func
        attribute calculation function for leaf node.
    """
    if node.is_leaf():
        # when recursion reaches leaf level, compute the attribute for each sensor
        # and store it as node.attribute[attribute]
        node.attribute[attr_name] = attr_func(node)

    else:
        # when recursion reach levels upper than stance
        # recursively call its branches to compute the branches' attribute
        # when recursion returns, average all branches' attribute as its node.sensor_peak
        branch_attribute_list = []
        for branch in node.branches():
            attribute_average_up(branch, attr_name, attr_func)
            branch_attribute_list.append(branch.attribute[attr_name])
        branch_sensor_peak = pd.concat(branch_attribute_list, axis=1)
        node.attribute[attr_name] = branch_sensor_peak.mean(axis=1)


def print_shapes(node: Type[pedarnode.PedarNode]):
    """Recursively print the structure tree and the leaf nodes' data frame shapes.
    
    Parameters
    ---
    node
        root node of the node tree.
    """
    if node.is_leaf():
        # when recursion reaches leaf level, print the data frame's shape
        print(' ' * node.level + str(node.name) + str(node.df.shape))

    else:
        # when recursion reach levels upper than leaf level
        # print its name with indents
        print(' ' * node.level + str(node.name))

        for branch in node.branches():
            print_shapes(branch)