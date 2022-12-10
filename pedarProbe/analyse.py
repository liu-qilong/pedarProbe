from __future__ import annotations
from typing import Type, Union

import pandas as pd

#from node import Leaf_Node
import node as no

def stance_peak(stance_node):
    """ compute the peak pressure of a stance """
    return stance_node.df.max()


def stance_pti(stance_node):
    """ compute the pressure-time integral of a stance """
    time_unit = stance_node.df.index[1] - stance_node.df.index[0]
    pt = stance_node.df * time_unit
    pti = pt.sum()
    return pti


def attribute_average_up(node, attr_name='sensor_peak', func_attr=stance_peak):
    """ recursively compute the attribute for each sensor among stance and average it up towards different feet, times, conditions, subjects level. """
    if type(node) is no.Leaf_Node:
        # when recursion reaches leaf level, compute the attribute for each sensor
        # and store it as node.attribute[attribute]
        node.attribute[attr_name] = func_attr(node)

    else:
        # when recursion reach levels upper than stance
        # recursively call its branches to compute the branches' attribute
        # when recursion returns, average all branches' attribute as its node.sensor_peak
        branch_attribute_list = []
        for branch in node.branches():
            attribute_average_up(branch, attr_name, func_attr)
            branch_attribute_list.append(branch.attribute[attr_name])
        branch_sensor_peak = pd.concat(branch_attribute_list, axis=1)
        node.attribute[attr_name] = branch_sensor_peak.mean(axis=1)


def print_shapes(node):
    """ recursively print the structure tree and the leaf's data frame shape. """
    level = len(node.loc) - 1

    if type(node) is no.Leaf_Node:
        # when recursion reaches leaf level, print the data frame's shape
        print(' ' * level + str(node.name) + str(node.df.shape))

    else:
        # when recursion reach levels upper than leaf level
        # print its name with indents
        print(' ' * level + str(node.name))

        for branch in node.branches():
            print_shapes(branch)