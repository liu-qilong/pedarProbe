"""Experimental data is usually stored in a multi-layer way, which cast server difficulty to effectively aggregate them and implement analysis. In a typical pedar data folder, data separate in various files can be identified as a 5 layer structure: :code:`subject - condition - trail - foot - stance`.

To formulate a universal framework for data analysis, it's an appealing choice to build a node trees that consist of these layers to store the data.

.. note::
    Python dictionary is very convenient for creating node tree: every dictionary object is a node in the node tree, and its branch nodes are added as a value to the dictionary, with its name as the keyword, layer by layer. In this case, any node in the node tree can be called in the format: :code:`root[subject][condition][trail][foot][stance]`. However, unlike other python object, it's not convenient to add new attributes to it. Therefore a dictionary object is not capable to realise all required features of a node tree, in respect to the classical computer science's view.

For this reason, various classes are developed supporting for construction of the data analysis workflow:

- :class:`Node` class is derived from the dictionary class :class:`Dict` to realised the basic node's features.
- :class:`DynamicNode` is derived from :class:`Node` to realised the layer layout restructuring feature.
- :class:`PedarNode` is derived from :class:`DynamicNode` conveying pedar data analysis and result aggregation through the whole node tree.
- :class:`DataNode` is derived from :class:`PedarNode` which is actually the leaf node of the node tree, storing the raw data prepared for analysis.

Tip
---
Such framework can be easily transferred for other data analysis task, especially the :class:`Node` and :class:`DynamicNode` which were developed in a highly generalisable way.
"""
from __future__ import annotations
from typing import Type, Union, Iterable, Dict

import copy
import pandas as pd

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

    Example
    ---
    ::

            import pedarProbe as pp
            n1 = pp.node.Node()
            n1.setup('S4')

            n2 = pp.node.Node()
            n2.setup('fast walking')

            n1.add_branch(n2)
            n1.print()  # print the node tree starting from n1
            n1['fast walking'].print()  # print the node tree starting from n2
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
        A :class:`list` must be passed to :attr:`nodes`. Otherwise the class may use :attr:`nodes` created in the last call of :meth:`collect_leaf` as the initial value, which may cause incorrect result.

        Example
        ---
        ::

            leafs = n1.collect_leaf(nodes=[])
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

        Example
        ---
        ::

            n1.print()
        """
        print(' ' * self.level + str(self.name))

        for branch in self.branches():
            branch.print()


# default loc map
default_loc_map = {
    'root': 0,
    'subject': 1, 
    'condition': 2,
    'trail': 3,
    'foot': 4,
    'stance': 5,
}


class DynamicNode(Node):
    """Derived from :class:`Node` to realised the layer layout restructuring feature (:meth:`restructure`).

    Note
    ---
    `Class Attributes`

    self.loc_map
        A dictionary that stores the layer names and its corresponding :attr:`level`, which is also its index in :attr:`self.loc`.
        
        With the :attr:`self.loc`, the :class:`Node` stores the information of its upper nodes in the node tree. However, to implement layer layout restructuring, it's necessary to be aware of the structure of its lower nodes' layout.

        Pursuing this goal, in :class:`DynamicNode` every layer of the whole node tree (from the root node) is designated with a name and the corresponding :attr:`level` value is stored in :attr:`self.loc_map`. Therefore, the :class:`DynamicNode` is aware of the structure of the whole node tree. The default value of :attr:`self.loc_map`: ::

            self.loc_map = {
                'root': 0,
                'subject': 1, 
                'condition': 2,
                'trail': 3,
                'foot': 4,
                'stance': 5,
            }
    """
    def setup(self, *args, **kwargs):
        """Compared with :meth:`~pedarProbe.node.Node.setup` of the base class :class:`Node`, initialisation of the :attr:`self.loc_map` is added."""
        Node.setup(self, *args, **kwargs)
        self.loc_map = default_loc_map

    # judgement
    def is_layer(self, layer: str) -> bool:
        """Judgment of whether the node belongs to a specific layer.

        Parameters
        ---
        layer
            name of the layer.
        
        Return
        ---
        :class:`bool`
            :code:`True` or :code:`False`
        """
        layer_level = self.loc_map[layer]
        return self.level == layer_level

    # access attribute
    def layer_layout(self) -> tuple:
        """Get the layer layout representation of the node tree starting from this node.
        
        Return
        ---
        :class:`tuple`
            From left to right stores the names of layers of this node, the branch nodes, the branch nodes' branch nodes, and so on, down to the leaf node level.
            
            For example, in the default layout, call :meth:`layer_layout` of the :code:`trail` layer node will return: :code:`('trail', 'foot', 'stance')`.

        Attention
        ---
        The layer layout representation is also used for indicating the way to restructure the node tree in :meth:`restructure`.
        """

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

    def collect_layer(self, layer: str, nodes: list) -> Iterable[Type[DynamicNode]]:
        """In the node tree starting from this node, recursively collect all nodes of a specific layer.

        Parameters
        ---
        layer
            name of the layer.
        nodes
            A list that will stores the collected nodes. If it's not empty, newly collected nodes will be append to it without erasing the existing items.
        
        Return
        ---
        :class:`list`
            A list of the collected nodes.

        Warning
        ---
        A :class:`list` must be passed to :attr:`nodes`. Otherwise the class may use :attr:`nodes` created in the last call of :meth:`collect_leaf` as the initial value, which may cause incorrect result.

        Example
        ---
        ::

            nodes = n1.collect_layer(layer='stance', nodes=[])
        """
        if self.is_layer(layer):
            # when recursion reaches leaf level, print the data frame's shape
            nodes.append(self)

        else:
            for branch in self.branches():
                nodes = branch.collect_layer(layer, nodes)
        
        return nodes

    # manipulation
    def change_loc_map(self, start_level: int, layout: str):
        """Change :attr:`loc_map` with a restructured layer layout representation.

        Parameters
        ---
        start_level
            the start level of restructuring.
        layout
            the restructured layer layout representation.
            
            .. tip::
                For more information see :meth:`layer_layout`.

        Attention
        ---
        This method is automatically called in :meth:`restructure`.
        """
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

    def restructure(self, layout: tuple = ('root', 'subject', 'condition', 'trail', 'foot', 'stance')) -> Type[DynamicNode]:
        """Return the restructured the node tree from this node.

        Attention
        ---
        The restructured the node tree is return, while the original node tree remains unchanged. This design is based on the fact that, in restructuring, some layers may be compress (aka flatten). In this case, the restructuring is irreversible, therefore it's better to keep the original node tree as a backup.
        
        Parameters
        ---
        layout
            the restructured layer layout representation.
            
            .. tip::
                For more information see :meth:`layer_layout`.

        Example
        ---
        To implement the node tree restructuring, it's better to check the layer layout of the node to be restructured: ::

            print(n1.layer_layout)

        For example, :code:`('root', 'subject', 'condition', 'trail', 'foot', 'stance')`. Assume that we'd like to make :code:`'condition'` layer directly under :code:'root' layer, compress all other layer as one layer, and named the compressed layer as :code:`'compress'`: ::

            n2 = n1.restructure(layout=('root', 'condition', 'compress'))

        Now we have the restructured :attr:`n2` and the original :attr:`n1` remains unchanged.

        """
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
    """Derived from :class:`DynamicNode` to provide pedar data analysis feature.

    In this project, :mod:`pedarProbe.analyse` provides functionalities for data analysis and :mod:`pedarProbe.export` provides functionalities for result export. :class:`PedarNode` conveys a bunch of short-cut functions to facilitate the usability.

    Note
    ---
    `Class Attributes`

    self.attributes :class:`dict`
        Dictionary of the analysed attributes, for example: ::

            self.attributes['sensor_peak']  # peak pressure
            self.attributes['pti']  # pressure-time integral

    Warning
    ---
    The specific attribute is only available after calling the corresponding analysis method.

    Attention
    ---
    In the returned node tree of restructuring (:meth:`~pedarProbe.node.DynamicNode.restructure`), all nodes' :attr:`self.attributes` will be erased. This design is based on the fact that different layer layouts usually leads to different analysis results, therefore there is no reason for keeping old analysis results.
    """
    def setup(self, *args, **kwargs):
        """Compared with :meth:`~pedarProbe.node.DynamicNode.setup` of the base class :class:`DynamicNode`, initialisation of the :attr:`self.attributes` is added."""
        DynamicNode.setup(self, *args, **kwargs)
        self.attribute = {}

    # data analysis
    def sensor_peak(self, is_export=False, export_layer: str = 'root', export_folder='output', save_suffix: str = ''):
        """Analyse the peak pressure of each sensor in the leaf node level, and then average up layer by layer up to the this node. Then for each node under this node, the peak pressure analysis result can be accessed with :code:`self.attributes['sensor_peak']`.
        
        Parameters
        ---
        is_export
            export the analysed result as a local file or not.
        export_layer
            if export as local file, the name of the layer to export.
        export_folder
            the folder of the exported file.
        save_suffix
            the suffix added to the default export file name :code:`sensor_peak`.

            .. tip::
                A specific suffix can avoid exported file be override by future export.

        Example
        ---
        ::

            n1.sensor_peak(
                is_export=True, 
                export_layer='condition', 
                export_folder='output', 
                save_suffix='_1213'  # export file name: sensor_peak_1213.xlsx
            )
        """
        # compute average peak pressure through data tree recursively
        # for each level, (average) peak pressure is stored as node.sensor_peak
        analyse.attribute_average_up(self, 'sensor_peak', analyse.sensor_peak)
        if is_export:
            export.attribute_batch_export(self, 'sensor_peak', export_layer, export_folder, save_suffix)

    def sensor_pti(self, is_export=False, export_layer: str = 'root', export_folder='output', save_suffix: str = ''):
        """Analyse the pressure-time integral (PTI) of each sensor in the leaf node level, and then average up layer by layer up to the this node. Then for each node under this node, the PTI analysis result can be accessed with :code:`self.attributes['sensor_pti']`.
        
        Parameters
        ---
        is_export
            export the analysed result as a local file or not.
        export_layer
            if export as local file, the name of the layer to export.
        export_folder
            the folder of the exported file.
        save_suffix
            the suffix added to the default export file name :code:`sensor_pti`.

            .. tip::
                A specific suffix can avoid exported file be override by future export.

        Example
        ---
        ::

            n1.sensor_pti(
                is_export=True, 
                export_layer='condition', 
                export_folder='output', 
                save_suffix='_1213'  # export file name: sensor_pti_1213.xlsx
            )
        """
        # compute average pressure-time integral through data tree recursively
        # for each level, (average) pressure-time integral is stored as node.sensor_peak
        analyse.attribute_average_up(self, 'sensor_pti', analyse.sensor_pti)

        if is_export:
            export.attribute_batch_export(self, 'sensor_pti', export_layer, export_folder, save_suffix)

    def heatmap(self, attr_name: str = 'sensor_peak', mask_dir: str = 'data/left_foot_mask.png', range: Union[str, tuple] = 'static', is_export: bool = False, export_folder: str = 'output', save_suffix: str = '') -> export.FootHeatmap:
        """Generate, plot, and export the heatmap for an attribute.
        
        Parameters
        ---
        attr_name
            name of the attribute, same as its keyword in :attr:`self.attributes`.
        mask_dir
            directory of the mask file.
            
            .. tip::
                If Python interpretor is run at the same directory as :code:`node.py`, :attr:`mask_dir` should be :code:`data/left_foot_mask.png`, i.e. the default value.

        is_export
            export the analysed result as a local file or not.
        export_layer
            if export as local file, the name of the layer to export.
        export_folder
            the folder of the exported file.
        save_suffix
            the suffix added to the default export file name :code:`foot_heatmap`.

            .. tip::
                A specific suffix can avoid exported file be override by future export.

        Return
        ---
        :class:`pedarProbe.export.FootHeatmap`
            heatmap object that can be further used or manipulated.

        Example
        ---
        ::

            n1.heatmap(
                is_export=True,  
                export_folder='output', 
                save_suffix='_1213'  # export file name: foot_heatmap_1213.png
            )
        """
        hm = export.FootHeatmap(self, attr_name, mask_dir)
        hm.export_foot_heatmap(range, is_export, export_folder, save_suffix)
        return hm


class DataNode(PedarNode):
    """Derived from :class:`PedarNode` which is actually the leaf node of the node tree, storing the raw data prepared for analysis.
    
    Note
    ---
    `Class Attributes`
    
    self.df :class:`pandas.core.frame.DataFrame`
        :mod:`Pandas` data frame that stores the sensor value of within a selected stance.
        Columns of the :attr:`self.df` is the sensor ID, from 0 ~ 98 belongs to the left foot and form 99 ~ 197 belongs to the right foot. It can be accessed with: ::
            
            self.df.columns

        Rows of the :attr:`self.df` is the time value, . It can be accessed with: ::
            
            self.df.index

        To access a data item with specific sensor id and time: ::
            
            id = 188
            time = 1.58
            self.df[id][time]

    self.start :class:`float`
        the start time of the selected stance.
    self.end :class:`float`
        the end time of the selected stance.
    """
    def setup(self, df: pd.DataFrame, start: float, end: float, *args, **kwargs):
        """Compared with :meth:`~pedarProbe.node.PedarNode.setup` of the base class :class:`PedarNode`, initialisations of the :attr:`self.df`, :attr:`self.start`, and :attr:`self.end` are added."""
        PedarNode.setup(self, *args, **kwargs)
        self.df = df
        self.start = start
        self.end = end