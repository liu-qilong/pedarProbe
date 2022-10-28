import re
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
        self.level = 0  # before added as other node's branch, the node is seen as root node in default
        self.attribute = {} # empty dictionary for storing analysed attributes, e.g. peak pressure

    def add_branch(self, branch_node):
        self[branch_node.name] = branch_node
        branch_node.set_source(self)
        branch_node.level = self.level + 1

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
        the same trail's information in the same condition and time is seperated in different entries
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

        # store the asc file object to self.trails[condition][time] node
        asc_object = pedar.Pedar_asc('{}/{}/{}.asc'.format(self.folder, self.name, asc))
        self[condition][time].asc = asc_object

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

                stance_node = Stance_Node()
                stance_node.setup(df, start, end, name=idx + 1)
                self[condition][time][foot].add_branch(stance_node)

            except:
                print('FATAL when add trail {} {} {} {} {}'.format(self.name, condition, time, foot, stance))


class Stance_Node(Node):
    def setup(self, df, start, end, *args, **kwargs):
        Node.setup(self, *args, **kwargs)
        self.df = df
        self.start = start
        self.end = end

    def compute_peak():
        pass