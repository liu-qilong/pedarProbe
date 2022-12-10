from __future__ import annotations
from typing import Type, Union, Iterable

import re
import copy
from typing import Dict

import parse
import analyse
import export

class Node(Dict):
    """
    python dictionary object is very convenient for creating node tree
    it can call any node in the format: root[branch][sub_branch]...[leaf]

    but unlike other python object, it's not convenient to add new attributes
    while adding customised processing/analysing function for different node levels and adding attributes accordingly is crucial
    so a node class was derived from the dictionary class to enhance its ability
    """
    def setup(self, name=None):
        """
        since the dictionary's __init__() is different from ordinary python class
        the init procedure are implemented in setup()
        without calling setup(), the node object doesn't provide full features of a node
        in the context of computer science
        """
        self.name = name
        self.level = 0
        self.loc = [name, ]
        self.attribute = {} # empty dictionary for storing analysed attributes, e.g. peak pressure

    def add_branch(self, branch_node: Type[Node]) -> Type[Node]:
        if branch_node.name in self.branch_names():
            print("warning: node [{}] already in node {}'s branch list".format(branch_node.name, str(self.loc)))

        self[branch_node.name] = branch_node
        branch_node.set_source(self)
        branch_node.loc = copy.deepcopy(self.loc)
        branch_node.loc.append(branch_node.name)
        branch_node.level = len(branch_node.loc) - 1

    def set_source(self, source_node):
        self.source = source_node

    def branch_names(self):
        return self.keys()

    def branches(self):
        return self.values()

    def is_leaf(self):
        return len(self.branch_names()) == 0

    def print_shapes(self):
        """ recursively print the structure tree and the leaf's data frame shape. """
        print(' ' * self.level + str(self.name))

        for branch in self.branches():
            branch.print_shapes()


class Pedar_Node(Node):
    def sensor_peak(self, is_export=True, export_folder='output'):
        # compute average peak pressure through data tree recursively
        # for each level, (average) peak pressure is stored as node.sensor_peak
        analyse.attribute_average_up(self, attr_name='sensor_peak', func_attr=analyse.stance_peak)

        if is_export:
            export.export_conditions_attribute(self, 'sensor_peak', export_folder)

    def sensor_pti(self, is_export=True, export_folder='output'):
        # compute average pressure-time integral through data tree recursively
        # for each level, (average) pressure-time integral is stored as node.sensor_peak
        analyse.attribute_average_up(self, attr_name='sensor_pti', func_attr=analyse.stance_pti)

        if is_export:
            export.export_conditions_attribute(self, 'sensor_pti', export_folder)

    def restructure(self, layers: tuple = ('subject', 'condition', 'time', 'foot', 'stance')) -> Type[Node]:
        # collect all leaf nodes
        def collect_leaf(node: Type[Node], leaf_nodes: list = []) -> Iterable[Data_Node]:
            if node.is_leaf():
                # when recursion reaches leaf level, print the data frame's shape
                leaf_nodes.append(node)

            else:
                for branch in node.branches():
                    leaf_nodes = collect_leaf(branch, leaf_nodes)
            
            return leaf_nodes

        leaf_nodes = collect_leaf(self)

        # prepare layer index dictionary for access data in node.loc
        layer2index = {
            'subject': 1,
            'condition': 2,
            'time': 3,
            'foot': 4,
            'stance': 5,
        }

        # for full layers structure, dismiss the last one
        # since, in this case, the last layer can be automatically identified
        if len(layers) == 5:
            layers = layers[:-1]

        # create root node
        root_node = Pedar_Node()
        root_node.setup('subjects')

        # parse each leaf node to construct the new node tree
        for leaf in leaf_nodes:
            loc = copy.deepcopy(leaf.loc)
            loc[0] = None
            current_node = root_node

            # add layer to the node tree as instructed
            for layer in layers:
                name = loc[layer2index[layer]]
                loc[layer2index[layer]] = None  # remove the used layer name
                
                if name not in current_node.branch_names():
                    branch_node = Node()
                    branch_node.setup(name)
                    current_node.add_branch(branch_node)
                    
                current_node = current_node[name]
            
            # the unused layers' names are combined as the new leaf node's name
            loc = [str(item) for item in loc if item is not None]
            leaf_name = '-'.join(loc)

            # construct the new leaf node and add it to the node tree
            leaf_node = Data_Node()
            leaf_node.setup(name=leaf_name, df=leaf.df, start=leaf.start, end=leaf.end)
            current_node.add_branch(leaf_node)
        
        return root_node


class Data_Node(Node):
    def setup(self, df, start, end, *args, **kwargs):
        Node.setup(self, *args, **kwargs)
        self.df = df
        self.start = start
        self.end = end