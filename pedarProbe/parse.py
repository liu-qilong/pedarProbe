"""Loading and parsing pedar plantar pressure data and construct a data node tree for further analysis.

Example
---
::

    from pedarProbe import parse

    condition_list = ['fast walking', 'slow walking', 'normal walking']
    data = parse.trails_parse(
        "data/subjects/walking plantar pressure time slot.xlsx",  # the guiding file's path
        condition_list,  # condition list will be used for format checking
        # max_read_rate=0.1,
    )
"""

from __future__ import annotations
from typing import Type, Union

import re
import sys
import numpy as np
import pandas as pd

from node import PedarNode, DataNode

class Pedar_asc(object):
    """Reader for :code:`.asc` file exported from pedar.
    
    Parameters
    ---
    path
        path of the :code:`.asc` file exported from pedar.
    skiprows
        number of rows to be skipped in file reading.
    header
        the index of row to be set as :attr:`self.doc`'s header.
    index_col
        the index of column to be set as the :attr:`self.doc`'s index.

    Note
    ---
    `Class Attributes`

    self.path :class:`str`
        path of the :code:`.asc` file exported from pedar.
    self.doc :class:`pandas.core.frame.DataFrame`
        loaded data frame, with sensor IDs as the columns (0~98 for left foot and 99 ~ 197 for the right foot) and time values as the rows.

        .. tip::
            There are two sensor ID numbering conventions. Please refer to :meth:`id_map` for more information.
    """
    def __init__(self, path: str, skiprows : int = 9, header : int = 9, index_col : int = 0):
        names = [idx for idx in range(199)]
        self.path = path
        self.doc = pd.read_csv(self.path, delimiter='\t', skiprows=skiprows, header=header, names=names, index_col=index_col)

        # column length check
        if self.doc.shape[1] != 199:
            print("\n{}'s dataframe has abnormal shape".format(path))

    def id_map(self, foot: str, sensor_id: int) -> int:
        """Maps sensor ID numbering from pedar convention to :mod:`pedarProbe` convention:

        - pedar convention: for each foot, sensors are numbered as 1~99.
        - :mod:`pedarProbe` convention: 0~98 for left foot sensors and 99 ~ 197 for the right foot sensors.
        
        Parameters
        ---
        foot
            :code:`'L'` as left foot and :code:`'R'` as right foot.
        sensor_id
            sensor ID in pedar convention.

        Return
        ---
        :class:`int`
            sensor ID in :mod:`pedarProbe` convention.
        """
        if foot == 'L' or foot == 'l':
            # left foot sensor 1~99 map to column 0~98
            return sensor_id - 1
        elif foot == 'R' or foot == 'r':
            # right foot sensor 1~99 map to column 99~197
            return sensor_id + 98
        else:
            print('invalid foot type when enquiry {}'.format(self.path))

    def get_time_sensor(self, foot: str, time: float, sensor_id: int) -> np.float64:
        """Get value with time and sensor ID.

        Parameters
        ---
        foot
            :code:`'L'` as left foot and :code:`'R'` as right foot.
        time
            time value.
        sensor_id
            sensor ID in pedar convention.

        Return
        ---
        :class:`numpy.float64`
        """
        return self.doc.loc[time, self.id_map(foot, sensor_id)]

    def get_time_seq(self, foot: str, time: float, start_sensor_id: int, end_sensor_id: int) -> pd.core.series.Series:
        """Get a sequence of values with time and start & end sensor IDs.

        Parameters
        ---
        foot
            :code:`'L'` as left foot and :code:`'R'` as right foot.
        time
            time value.
        start_sensor_id
            start sensor ID in pedar convention.
        end_sensor_id
            end sensor ID in pedar convention.

        Return
        ---
        :class:`pandas.core.series.Series`
        """
        return self.doc.loc[time, self.id_map(foot, start_sensor_id):self.id_map(foot, end_sensor_id)]
    
    def get_sensor_seq(self, foot: str, sensor_id: int, start_time: float, end_time: float) -> pd.core.series.Series:
        """Get a sequence of values with sensor ID and start & end time.

        Parameters
        ---
        foot
            :code:`'L'` as left foot and :code:`'R'` as right foot.
        sensor_id
            start sensor ID in pedar convention.
        start_time
            start time value.
        end_time
            end time value.

        Return
        ---
        :class:`pandas.core.series.Series`
        """
        return self.doc.loc[start_time:end_time, self.id_map(foot, sensor_id)]

    def get_time_sensor_slice(self, foot: str, start_time: float, end_time: float, start_sensor_id: int = 1, end_sensor_id: int = 99) -> pd.core.frame.DataFrame:
        """Get a frame of values with start & end sensor IDs and start & end time.

        Parameters
        ---
        foot
            :code:`'L'` as left foot and :code:`'R'` as right foot.
        start_sensor_id
            start sensor ID in pedar convention.
        end_sensor_id
            end sensor ID in pedar convention.
        start_time
            start time value.
        end_time
            end time value.

        Return
        ---
        :class:`pandas.core.frame.DataFrame`
        """
        return self.doc.loc[start_time:end_time, self.id_map(foot, start_sensor_id):self.id_map(foot, end_sensor_id)]


def progress_bar(percent: float, bar_len: int = 20):
    """Print & refresh the progress bar in terminal.

    Parameters
    ---
    percent
        percentage from 0 to 1.
    bar_len
        length of the progress bar
    """
    sys.stdout.write("\r")
    sys.stdout.write("[{:<{}}] {:.1%}".format("=" * int(bar_len * percent), bar_len, percent))
    sys.stdout.flush()
    # avoiding '%' appears when progress completed
    if percent == 1:
        print()


def add_trail(node: PedarNode, asc: str, folder: str, condition: str, trail: str, foot: str, stances: list):
    """Construct node tree starting from a subject node according to information of an entry in the guiding file.

    Parameters
    ---
    node
        the subject node.
    asc
        the :code:`asc` file name.
    folder
        the folder of the :code:`asc` file.
    condition
        condition name.
    trail
        trail name.
    foot
        foot name.
    stances
        a list of stance timestamp string. Each item of :attr:`stances` is in the form of :code:`'<start_time>-<end_time>'`.

    Note
    ---
    The same subject's information in the same condition and trail is separated in different entries.Each of them contains one foot type with specific stances time stamp. Therefore the node tree is not constructed in one go. This function is developed to handle the incremental construction process.
    """
    if condition not in node.branch_names():
        condition_node = PedarNode()
        condition_node.setup(name=condition)
        node.add_branch(condition_node)
    
    if trail not in node[condition].branch_names():
        trail_node = PedarNode()
        trail_node.setup(name=trail)
        node[condition].add_branch(trail_node)

    # read asc file object
    asc_object = Pedar_asc('{}/{}/{}.asc'.format(folder, node.name, asc))

    # then filled foot and stances data, which complete the dictionary structure to
    # node[condition][trail][foot][stance]
    foot_node = PedarNode()
    foot_node.setup(name=foot)
    node[condition][trail].add_branch(foot_node)

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
        stance_node.setup(df, start, end, name='stance ' + str(idx + 1))
        node[condition][trail][foot].add_branch(stance_node)


def trails_parse(path: Union[None, str], condition_list: list, max_read_rate: float = 1.0):
    """Load and parse pedar plantar pressure data and return the constructed node tree according to the guiding file.
    
    Parameters
    ---
    path
        the path of the guiding file.
    condition_list
        a list of condition names.

        .. warning::
            It will be used for format checking for the entries in the guiding file.

    max_read_rate
        :attr:`max_read_rate` is the percentage from 0 ~ 1. Only load :attr:`max_read_rate` of entries.

        .. tip::
            Data loading is very time consuming. When developing new features, it may speed up the verification and debug by setting a low :attr:`max_read_rate`. ::

                from pedarProbe import parse

                condition_list = ['fast walking', 'slow walking', 'normal walking']
                data = parse.trails_parse(
                    "data/subjects/walking plantar pressure time slot.xlsx",  # the guiding file's path
                    condition_list,  # condition list will be used for format checking
                    max_read_rate=0.1,
    """
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
        trail = 'trail ' + re.search('[0-9]+$', asc).group()
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
        add_trail(root[subject_name], asc, folder, condition, trail, foot, stances)
        
        # print progress bar and break if exceed max read rate
        read_rate = (index + 1) / length
        progress_bar(read_rate)
        if read_rate >= max_read_rate:
            break

    return root