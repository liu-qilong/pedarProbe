import re
import sys
import pandas as pd

import node
import analyse
import export

class Pedar_asc(object):
    def __init__(self, path, skiprows=9, header=9, index_col=0):
        names = [idx for idx in range(199)]
        self.path = path
        self.doc = pd.read_csv(self.path, delimiter='\t', skiprows=skiprows, header=header, names=names, index_col=index_col)

    def id_map(self, foot, sensor_id):
        if foot == 'L' or foot == 'l':
            # left foot sensor 1~99 map to column 0~98
            return sensor_id - 1
        elif foot == 'R' or foot == 'r':
            # right foot sensor 1~99 map to column 99~198
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


class Trails_Parser(object):
    def __init__(self, path, condition_list):
        self.condition_list = condition_list
        self.generate_asc_pattern()

        self.doc = pd.read_excel(path)
        self.folder = re.search('^.*(?=/)', path).group()
        
        self.subjects = node.Node()
        self.subjects.setup('subjects')

        length = len(self.doc.index)
        print("loading {} data entries".format(length))
        for index in self.doc.index:
            # parse information of each trail
            asc = self.doc.loc[index, 'Unnamed: 0']
            asc_check = re.match(self.asc_pattern, asc)
            if not asc_check:
                print('invalid asc entry name: {}'.format(asc))
                break
            
            try:
                condition = re.search('(?<= )[a-z ]+(?= )', asc).group()
                time = int(re.search('[0-9]+$', asc).group())
                foot = self.doc.loc[index, 'sideFoot']
                stances = self.doc.loc[index, 'stance phase 1':]

                # parse the subject's name
                # if the subject hasn't been added to self.subjects dictionary, add it
                subject_name = re.search('^S[0-9]+', asc).group()
                if subject_name not in self.subjects.branch_names():
                    subject_node = node.Subject_Node()
                    subject_node.setup(name=subject_name, folder=self.folder)
                    self.subjects.add_branch(subject_node)
                
                # add a trial to the subject
                self.subjects[subject_name].add_trail(asc, condition, time, foot, stances)
                drawProgressBar((index + 1) / length)

            except:
                print('FATAL when parse the {}-th entry: {}'.format(index + 1, asc))

    def generate_asc_pattern(self):
        conditions = '|'.join(self.condition_list)
        self.asc_pattern = 'S[1-9][0-9]* (' + conditions + ') [1-9][0-9]*$'

    def sensor_peak(self, is_export=True, export_folder='result'):
        # compute average peak pressure through data tree recursively
        # for each level, (average) peak pressure is stored as node.sensor_peak
        for subject in self.subjects.branches():
            analyse.sensor_peak(subject)

        if is_export:
            export.export_sensor_peak(self.subjects, export_folder)


def drawProgressBar(percent, barLen = 20):
    """ percent float from 0 to 1 """
    sys.stdout.write("\r")
    sys.stdout.write("[{:<{}}] {:.1%}".format("=" * int(barLen * percent), barLen, percent))
    sys.stdout.flush()
    # avoiding '%' appears when progress completed
    if percent == 1:
        print()


if __name__ == "__main__":
    condition_list = ['fast walking', 'slow walking', 'normal walking']
    data = Trails_Parser("subjects/walking plantar pressure time slot.xlsx", condition_list)