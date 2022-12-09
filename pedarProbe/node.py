from __future__ import annotations
from typing import Type, Union

import re
import copy
from typing import Dict

import pedar

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
        self.loc = [name, ]
        self.attribute = {} # empty dictionary for storing analysed attributes, e.g. peak pressure

    def add_branch(self, branch_node):
        self[branch_node.name] = branch_node
        branch_node.set_source(self)
        branch_node.loc = copy.deepcopy(self.loc)
        branch_node.loc.append(branch_node.name)

    def set_source(self, source_node):
        self.source = source_node

    def branch_names(self):
        return self.keys()

    def branches(self):
        return self.values()


class Subject_Node(Node):
    def setup(self, folder, *args, **kwargs):
        Node.setup(self, *args, **kwargs)
        self.folder = folder

    def add_trail(self, asc, condition, time, foot, stances):
        """
        the same trail's information in the same condition and time is separated in different entries
        each one contains one foot type with stances timestamp
        therefore firstly construct the self.trails[condition][time] dictionary construction
        """
        if condition not in self.branch_names():
            condition_node = Node()
            condition_node.setup(name=condition)
            self.add_branch(condition_node)
        
        if time not in self[condition].branch_names():
            time_node = Node()
            time_node.setup(name=time)
            self[condition].add_branch(time_node)

        # read asc file object
        asc_object = pedar.Pedar_asc('{}/{}/{}.asc'.format(self.folder, self.name, asc))

        # then filled foot and stances data, which complete the dictionary structure to
        # self[condition][time][foot][stance]
        foot_node = Node()
        foot_node.setup(name=foot)
        self[condition][time].add_branch(foot_node)

        for idx in range(len(stances)):
            try:
                stance = stances[idx]

                # skip empty/invalid stance
                # since the data of some empty stances are int, transform it to str in advance
                if not re.search('[1-9][0-9\.]*-[1-9][0-9\.]*', str(stance)):
                    continue

                start = float(re.search('^[0-9\.]+[^-]', stance).group())
                end = float(re.search('[^-][0-9\.]+$', stance).group())
                df = asc_object.get_time_sensor_slice(foot, start, end)

                stance_node = Leaf_Node()
                stance_node.setup(df, start, end, name=idx + 1)
                self[condition][time][foot].add_branch(stance_node)

            except:
                print('FATAL when add trail {} {} {} {} {}'.format(self.name, condition, time, foot, stance))


class Leaf_Node(Node):
    def setup(self, df, start, end, *args, **kwargs):
        Node.setup(self, *args, **kwargs)
        self.df = df
        self.start = start
        self.end = end

    def compute_peak():
        pass


def node_restructure(node: Type[Node], layers: tuple = ('subject', 'condition', 'time', 'foot', 'stance')) -> Type[Node]:
    # collect all leaf nodes
    def collect_leaf(node: Type[Node], leaf_nodes: list = []) -> Iterable[Leaf_Node]:
        if type(node) is Leaf_Node:
            # when recursion reaches leaf level, print the data frame's shape
            leaf_nodes.append(node)

        else:
            for branch in node.branches():
                leaf_nodes = collect_leaf(branch, leaf_nodes)
        
        return leaf_nodes

    leaf_nodes = collect_leaf(node)

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
    root_node = Node()
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
            
            branch_node = Node()
            branch_node.setup(name)
            
            current_node.add_branch(branch_node)
            current_node = branch_node
        
        # the unused layers' names are combined as the new leaf node's name
        loc = [str(item) for item in loc if item is not None]
        leaf_name = '-'.join(loc)

        # construct the new leaf node and add it to the node tree
        leaf_node = Leaf_Node()
        leaf_node.setup(name=leaf_name, df=leaf.df, start=leaf.start, end=leaf.end)
        current_node.add_branch(leaf_node)
    
    return root_node