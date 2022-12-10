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
            print(self.branch_names())
            print("warning: node [{}] already in node {}'s branch list".format(branch_node.name, str(self.loc)))
            return

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

    def is_level(self, layer):
        layer_level = self.loc_map[layer]
        return self.level == layer_level

    def print(self):
        """ recursively print the structure tree and the leaf's data frame shape. """
        print(' ' * self.level + str(self.name))

        for branch in self.branches():
            branch.print()

    def clean_copy(self) -> Type[Node]:
        new_node = self.__class__()
        new_node.setup(self.name)
        new_node.loc = copy.deepcopy(self.loc)
        new_node.level = copy.deepcopy(self.level)
        return new_node

    def collect_layer(node: Type[Node], layer: str, nodes: list) -> Iterable[Type[Node]]:
        if node.is_level(layer):
            # when recursion reaches leaf level, print the data frame's shape
            nodes.append(node)

        else:
            for branch in node.branches():
                nodes = branch.collect_layer(layer, nodes)
        
        return nodes

    def collect_leaf(self, nodes: list) -> Iterable[Data_Node]:
        if self.is_leaf():
            # when recursion reaches leaf level, print the data frame's shape
            nodes.append(self)

        else:
            for branch in self.branches():
                nodes = branch.collect_leaf(nodes)
        
        return nodes


class Pedar_Node(Node):
    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)

        self.loc_map = {
            'root': 0,
            'subject': 1, 
            'condition': 2,
            'time': 3,
            'foot': 4,
            'stance': 5,
        }

    def change_loc_map(self, start_level, layers):
        # calculate the index in loc of the first layer to be changed
        start_index = start_level + 1

        # delete the layers from the first layer to be changed
        del_keys = []
        for key, value in self.loc_map.items():
            if value >= start_index:
                del_keys.append(key)
        
        for key in del_keys:
            del self.loc_map[key]

        # change the layer indexes as instructed
        num_layer_change = len(layers)

        for idx in range(num_layer_change):
            layer = layers[idx]
            self.loc_map[layer] = start_index + idx

    def restructure(self, layers: tuple = ('subject', 'condition', 'time', 'foot', 'stance')) -> Type[Pedar_Node]:
        # collect all leaf nodes
        leaf_nodes = self.collect_leaf(nodes=[])

        # create node
        new_node = self.clean_copy()
        '''
        new_node = Pedar_Node()
        new_node.setup(self.name)
        new_node.loc = copy.deepcopy(self.loc)
        new_node.level = copy.deepcopy(self.level)
        '''
        new_node.change_loc_map(new_node.level, layers)

        # parse each leaf node to construct the new node tree
        for leaf in leaf_nodes:
            # loc is copied to generate name of the restructured layers
            # and the unused parts will be concatenated as the name of the leaf node
            loc = copy.deepcopy(leaf.loc)

            # set the layer upper than the self node as None since they won't be used
            for id in range(self.level + 1):
                loc[id] = None

            current_node = new_node

            # add layer to the node tree as instructed
            for layer in layers[:-1]:
                name = loc[leaf.loc_map[layer]]
                loc[leaf.loc_map[layer]] = None  # remove the used layer name
                
                if name not in current_node.branch_names():
                    branch_node = Pedar_Node()
                    branch_node.setup(name)
                    branch_node.change_loc_map(new_node.level, layers)
                    current_node.add_branch(branch_node)
                    
                current_node = current_node[name]

            # the unused layers' names are combined as the new leaf node's name
            loc = [str(item) for item in loc if item is not None]
            leaf_name = '-'.join(loc)

            # construct the new leaf node and add it to the node tree
            leaf_node = Data_Node()
            leaf_node.setup(name=leaf_name, df=leaf.df, start=leaf.start, end=leaf.end)
            leaf_node.change_loc_map(new_node.level, layers)
            current_node.add_branch(leaf_node)
        
        return new_node

    def sensor_peak(self, is_export=False, export_layer: str = 'root', export_folder='output', save_suffix: str = ''):
        # compute average peak pressure through data tree recursively
        # for each level, (average) peak pressure is stored as node.sensor_peak
        analyse.attribute_average_up(self, 'sensor_peak', analyse.stance_peak)
        if is_export:
            export.attribute_batch_export(self, 'sensor_peak', export_layer, export_folder, save_suffix)

    def sensor_pti(self, is_export=False, export_layer: str = 'root', export_folder='output', save_suffix: str = ''):
        # compute average pressure-time integral through data tree recursively
        # for each level, (average) pressure-time integral is stored as node.sensor_peak
        analyse.attribute_average_up(self, 'sensor_pti', analyse.stance_pti)

        if is_export:
            export.attribute_batch_export(self, 'sensor_pti', export_layer, export_folder, save_suffix)

    def heatmap(self, attr_name: str = 'sensor_peak', mask_dir: str = 'data/left_foot_mask.png', is_export: bool = False, range: Union[str, tuple] = 'static', export_folder: str = 'output', save_suffix: str = '') -> export.FootHeatmap:
        hm = export.FootHeatmap(self, attr_name, mask_dir)
        hm.export_foot_heatmap(is_export, range, export_folder, save_suffix)
        return hm


class Data_Node(Pedar_Node):
    def setup(self, df, start, end, *args, **kwargs):
        Node.setup(self, *args, **kwargs)
        self.df = df
        self.start = start
        self.end = end