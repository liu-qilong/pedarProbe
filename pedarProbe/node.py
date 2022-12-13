"""Experimental data is usually stored in a multi-level way, which cast server difficulty to effectively aggregate them and implement analysis. In a typical pedar data folder, data separate in various files can be identified as a 5 layer structure: :code:`subject - condition - time - foot - stance`.

To formulate a universal framework for data analysis, it's an appealing choice to build a node trees that consist of these layers to store the data.

.. note::
    
    Python dictionary is very convenient for creating node tree: every dictionary object is a node in the node tree, and its branch nodes are added as a value to the dictionary, with its name as the keyword, layer by layer. In this case, any node in the node tree can be called in the format: :code:`root[subject][condition][trail][foot][stance]`. However, unlike other python object, it's not convenient to add new attributes to it. Therefore a dictionary object is not capable to realise all required features of a node tree, in respect to the classical computer science's view.

For this reason, :class:`Node` class is derived from the dictionary class :class:`Dict` to realised the basic node's features. And the :class:`DynamicNode` is derived from :class:`Node` to realised the layer layout restructure feature. :class:`PedarNode` is derived from :class:`DynamicNode` conveying pedar data analysis and result aggregation through the whole node tree. And the :class:`DataNode` is derived from :class:`PedarNode` which is actually the leaf node of the node tree, storing the raw data prepared for analysis.
"""
from __future__ import annotations
from typing import Type, Union, Iterable

import copy
from typing import Dict

import analyse
import export

class Node(Dict):
    """:class:`Node` class is derived from the dictionary class :class:`Dict` to realised the basic node's features.
    
    Note
    ---
    `Class Attributes`

    self.name :class:`str`
        the name of the node.
    self.level :class:`int`
        the level of layer. The root node's :attr:`level` is 0, its branches' level are 1, and so on.
    self.loc :class:`list`
        from right to left, stores the names of the node, its source node, its source node's source node, and so on, up to the root node level. 
        
        For example, :code:`self.loc = ['root', 'S4', 'fast walking', 'trail 1', 'L', 'stance 2']`. It represents the location of the node in the node tree.
    """
    # init and change
    def setup(self, name: str = ''):
        """
        Since the dictionary's :meth:`__init__` method is different from ordinary python class, the initialisation procedure are implemented in :meth:`setup`.

        Parameters
        ---
        name
            the name of the node
        
        Warning
        ---
        Without calling :meth:`setup`, the node object doesn't provide full features of a node.

        Example
        ---
        ::

            import pedarProbe as pp
            n1 = pp.node.Node()
            n1.setup('S4')
        """
        self.name = name
        self.level = 0
        self.loc = [name, ]

    def add_branch(self, branch_node: Type[Node]) -> Type[Node]:
        """Add branch to the node.
        
        Parameters
        ---
        branch_node
            the node being added as a branch. Its name will be used as its keyword.
            
        Example
        ---
        ::

            import pedarProbe as pp
            n1 = pp.node.Node()
            n1.setup('S4')

            n2 = pp.node.Node()
            n2.setup('fast walking')

            n1.add_branch(n2)

        Then, the :attr:`n2` node can be accessed with its name: ::

            n1['fast walking']  # access n2

        Warning
        ---
        If the added node's name is already exist in the branch nodes name list, the newly added node will replace it, with a warning message presented to the prompt.
        """
        if branch_node.name in self.branch_names():
            print(self.branch_names())
            print("warning: node [{}] already in node {}'s branch list".format(branch_node.name, str(self.loc)))
            return

        self[branch_node.name] = branch_node
        branch_node.set_source(self)
        branch_node.loc = copy.deepcopy(self.loc)
        branch_node.loc.append(branch_node.name)
        branch_node.level = len(branch_node.loc) - 1

    def set_source(self, source_node: Type[Node]):
        """Set the source node of the node.
        
        Parameters
        ---
        source_node
            the node being set as the source branch

        Attention
        ---
        In most cases, the user doesn't need to use this method. In :meth:`add_branch`, when a node :attr:`n2` is set as node :attr:`n1`'s branch, :meth:`set_source` will be automatically called to set :attr:`n1` as :attr:`n2`'s source node.
        """
        self.source = source_node

    def clean_copy(self) -> Type[Node]:
        """Create and return a deep copy of the node only with its major attributes, including :attr:`name`, :attr:`loc`, and :attr:`level`.

        Returns
        ---
        :class:`Node`
            the clean deep copy of the node.

        Attention
        ---
        In the derived classes of :class:`Node`, the returned type are the derived classes, rather than the basic class :class:`Node`.
        """
        new_node = self.__class__()
        new_node.setup(self.name)
        new_node.loc = copy.deepcopy(self.loc)
        new_node.level = copy.deepcopy(self.level)
        return new_node

    # judgement
    def is_leaf(self) -> bool:
        """Judgment of whether the node is a leaf node or not.
        
        Return
        ---
        :class:`bool`
            :code:`True` or :code:`False`
        """
        return len(self.branch_names()) == 0

    # access attribute
    def branch_names(self) -> Iterable[str]:
        """Return a list of branch nodes' names.

        Return
        ---
        :class:`dict_keys`
        """
        return self.keys()

    def branches(self) -> Iterable[Type[Node]]:
        """Return a list of branch nodes objects.

        Return
        ---
        :class:`dict_values`
        """
        return self.values()

    def collect_leaf(self, nodes: list) -> Iterable[Node]:
        """Recursively collect all leaf nodes starting from this node.

        Parameters
        ---
        nodes
            A list that will stores the collected leaf nodes. If it's not empty, newly collected nodes will be append to it without erasing the existing items.
        
        Return
        ---
        :class:`list`
            A list of the collected leaf nodes.

        Warning
        ---
        A :class:`list` must be passed to :code:`nodes`. Otherwise the class may use :code:`nodes` created in the last call of :meth:`collect_leaf` as the initial value, which may cause incorrect result.

        Example
        ---
        ::

            leafs = n1.collect_leaf([])
        """
        if self.is_leaf():
            # when recursion reaches leaf level, print the data frame's shape
            nodes.append(self)

        else:
            for branch in self.branches():
                nodes = branch.collect_leaf(nodes)
        
        return nodes

    # inspection
    def print(self):
        """Recursively print the structure of the node tree starting from this node.
        """
        print(' ' * self.level + str(self.name))

        for branch in self.branches():
            branch.print()


default_layout = {
    'root': 0,
    'subject': 1, 
    'condition': 2,
    'trail': 3,
    'foot': 4,
    'stance': 5,
}


class DynamicNode(Node):
    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        self.loc_map = default_layout

    # judgement
    def is_layer(self, layer: str) -> bool:
        """Judgment of whether the node belongs to a specific layer.

        Parameters
        ---
        layer
            name of the layer
        
        Return
        ---
        :class:`bool`
            :code:`True` or :code:`False`
        """
        layer_level = self.loc_map[layer]
        return self.level == layer_level

    # access attribute
    def layer_layout(self) -> tuple:

        def get_max_value(d: dict):
            value_ls = list(d.values())
            return max(value_ls)

        def get_key_with_value(d: dict, value):
            for key, val in d.items():
                if val == value:
                    return key

        start_index = self.level
        end_index = get_max_value(self.loc_map)
        
        layer_ls = [get_key_with_value(self.loc_map, index) for index in range(start_index, end_index + 1)]
        return tuple(layer_ls)

    def collect_layer(node: Type[Node], layer: str, nodes: list) -> Iterable[Type[Node]]:
        if node.is_layer(layer):
            # when recursion reaches leaf level, print the data frame's shape
            nodes.append(node)

        else:
            for branch in node.branches():
                nodes = branch.collect_layer(layer, nodes)
        
        return nodes

    # manipulation
    def change_loc_map(self, start_level, layout):
        # calculate the index in loc of the first layer to be changed
        start_index = start_level

        # delete the layers from the first layer to be changed
        del_keys = []
        for key, value in self.loc_map.items():
            if value >= start_index:
                del_keys.append(key)
        
        for key in del_keys:
            del self.loc_map[key]

        # change the layer indexes as instructed
        num_layer_change = len(layout)

        for idx in range(num_layer_change):
            layer = layout[idx]
            self.loc_map[layer] = start_index + idx

    def restructure(self, layout: tuple = ('root', 'subject', 'condition', 'trail', 'foot', 'stance')) -> Type[PedarNode]:
        # collect all leaf nodes
        leaf_nodes = self.collect_leaf(nodes=[])

        # create node
        new_node = self.clean_copy()
        new_node.change_loc_map(new_node.level, layout)

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
            for layer in layout[1:-1]:
                name = loc[leaf.loc_map[layer]]
                loc[leaf.loc_map[layer]] = None  # remove the used layer name
                
                if name not in current_node.branch_names():
                    branch_node = PedarNode()
                    branch_node.setup(name)
                    branch_node.change_loc_map(new_node.level, layout)
                    current_node.add_branch(branch_node)
                    
                current_node = current_node[name]

            # the unused layers' names are combined as the new leaf node's name
            loc = [str(item) for item in loc if item is not None]
            leaf_name = ' - '.join(loc)

            # construct the new leaf node and add it to the node tree
            leaf_node = DataNode()
            leaf_node.setup(name=leaf_name, df=leaf.df, start=leaf.start, end=leaf.end)
            leaf_node.change_loc_map(new_node.level, layout)
            current_node.add_branch(leaf_node)
        
        return new_node

class PedarNode(DynamicNode):
    def setup(self, *args, **kwargs):
        DynamicNode.setup(self, *args, **kwargs)
        self.attribute = {} # empty dictionary for storing analysed attributes, e.g. peak pressure

    # data analysis
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


class DataNode(PedarNode):
    def setup(self, df, start, end, *args, **kwargs):
        PedarNode.setup(self, *args, **kwargs)
        self.df = df
        self.start = start
        self.end = end