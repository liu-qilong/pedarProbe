from __future__ import annotations
from typing import Type, Union

import re
import sys
import pandas as pd

from node import PedarNode, DataNode

class Pedar_asc(object):
    def __init__(self, path, skiprows=9, header=9, index_col=0):
        names = [idx for idx in range(199)]
        self.path = path
        self.doc = pd.read_csv(self.path, delimiter='\t', skiprows=skiprows, header=header, names=names, index_col=index_col)

        # column length check
        if self.doc.shape[1] != 199:
            print("\n{}'s dataframe has abnormal shape".format(path))

    def id_map(self, foot, sensor_id):
        if foot == 'L' or foot == 'l':
            # left foot sensor 1~99 map to column 0~98
            return sensor_id - 1
        elif foot == 'R' or foot == 'r':
            # right foot sensor 1~99 map to column 99~197
            return sensor_id + 98
        else:
            print('invalid foot type when enquiry {}'.format(self.path))

    def get_time_sensor(self, foot, time, sensor_id):
        return self.doc.loc[time, self.id_map(foot, sensor_id)]

    def get_time_seq(self, foot, time, start_sensor_id, end_sensor_id):
        return self.doc.loc[time, self.id_map(foot, start_sensor_id):self.id_map(foot, end_sensor_id)]
    
    def get_sensor_seq(self, foot, sensor_id, start_time, end_time):
        return self.doc.loc[start_time:end_time, self.id_map(foot, sensor_id)]

    def get_time_sensor_slice(self, foot, start_time, end_time, start_sensor_id=1, end_sensor_id=99):
        return self.doc.loc[start_time:end_time, self.id_map(foot, start_sensor_id):self.id_map(foot, end_sensor_id)]


def progress_bar(percent, barLen = 20):
    """ percent float from 0 to 1 """
    sys.stdout.write("\r")
    sys.stdout.write("[{:<{}}] {:.1%}".format("=" * int(barLen * percent), barLen, percent))
    sys.stdout.flush()
    # avoiding '%' appears when progress completed
    if percent == 1:
        print()


def add_trail(node, asc, folder, condition, time, foot, stances):
    """
    the same trail's information in the same condition and time is separated in different entries
    each one contains one foot type with stances timestamp
    therefore firstly construct the self.trails[condition][time] dictionary construction
    """
    if condition not in node.branch_names():
        condition_node = PedarNode()
        condition_node.setup(name=condition)
        node.add_branch(condition_node)
    
    if time not in node[condition].branch_names():
        time_node = PedarNode()
        time_node.setup(name=time)
        node[condition].add_branch(time_node)

    # read asc file object
    asc_object = Pedar_asc('{}/{}/{}.asc'.format(folder, node.name, asc))

    # then filled foot and stances data, which complete the dictionary structure to
    # node[condition][time][foot][stance]
    foot_node = PedarNode()
    foot_node.setup(name=foot)
    node[condition][time].add_branch(foot_node)

    for idx in range(len(stances)):
        stance = stances[idx]

        # skip empty/invalid stance
        # since the data of some empty stances are int, transform it to str in advance
        if not re.search('[1-9][0-9\.]*-[1-9][0-9\.]*', str(stance)):
            continue

        start = float(re.search('^[0-9\.]+[^-]', stance).group())
        end = float(re.search('[^-][0-9\.]+$', stance).group())
        df = asc_object.get_time_sensor_slice(foot, start, end)

        stance_node = DataNode()
        stance_node.setup(df, start, end, name=idx + 1)
        node[condition][time][foot].add_branch(stance_node)


def trails_parse(path: Union[None, str], condition_list, max_read_rate: float = 1.0):
    # generate entry pattern for format checking
    conditions = '|'.join(condition_list)
    asc_pattern = 'S[1-9][0-9]* (' + conditions + ') [1-9][0-9]*$'
    
    # create root node
    root = PedarNode()
    root.setup('root')

    # load the summary file
    doc = pd.read_excel(path)
    folder = re.search('^.*(?=/)', path).group()
    length = len(doc.index)
    print("loading {} data entries".format(length))

    # parse each entry
    for index in doc.index:
        # parse information of each trail
        asc = doc.loc[index, 'Unnamed: 0']
        asc_check = re.match(asc_pattern, asc)
        if not asc_check:
            print('invalid asc entry name: {}'.format(asc))
            break
        
        condition = re.search('(?<= )[a-z ]+(?= )', asc).group()
        time = int(re.search('[0-9]+$', asc).group())
        foot = doc.loc[index, 'sideFoot']
        stances = doc.loc[index, 'stance phase 1':]

        # parse the subject's name
        # if the subject hasn't been added to root dictionary, add it
        subject_name = re.search('^S[0-9]+', asc).group()

        if subject_name not in root.branch_names():
            subject_node = PedarNode()
            subject_node.setup(subject_name)
            root.add_branch(subject_node)
        
        # add a trial to the subject
        add_trail(root[subject_name], asc, folder, condition, time, foot, stances)
        
        # print progress bar and break if exceed max read rate
        read_rate = (index + 1) / length
        progress_bar(read_rate)
        if read_rate >= max_read_rate:
            break

    return root