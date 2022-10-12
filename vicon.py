import re
import sys
import pandas as pd

class Vicon_asc(object):
    def __init__(self, path, header=9, index_col=0):
        self.path = path
        self.doc = pd.read_csv(path, delimiter='\t', header=header, index_col=index_col)

    def get_time_sensor(self, foot, time, sensor_id):
        if foot == 'L' or foot == 'l':
            return self.doc.loc[time, str(sensor_id)]
        elif foot == 'R' or foot == 'r':
            return self.doc.loc[time, str(sensor_id) + '.1']
        else:
            print('invalid foot type when enquiry {}'.format(self.path))

    def get_time_seq(self, foot, time, start_sensor_id, end_sensor_id):
        if foot == 'L' or foot == 'l':
            return self.doc.loc[time, str(start_sensor_id):str(end_sensor_id)]
        elif foot == 'R' or foot == 'r':
            return self.doc.loc[time, str(start_sensor_id) + '.1':str(end_sensor_id) + '.1']
        else:
            print('invalid foot type when enquiry {}'.format(self.path))
    
    def get_sensor_seq(self, foot, sensor_id, start_time, end_time):
        if foot == 'L' or foot == 'l':
            return self.doc.loc[start_time:end_time, str(sensor_id)]
        elif foot == 'R' or foot == 'r':
            return self.doc.loc[start_time:end_time, str(sensor_id) + '.1']
        

    def get_time_sensor_slice(self, foot, start_time, end_time, start_sensor_id=1, end_sensor_id=99):
        if foot == 'L' or foot == 'l':
            return self.doc.loc[start_time:end_time, str(start_sensor_id):str(end_sensor_id)]
        elif foot == 'R' or foot == 'r':
            return self.doc.loc[start_time:end_time, str(start_sensor_id) + '.1':str(end_sensor_id) + '.1']
        else:
            print('invalid foot type when enquiry {}'.format(self.path))        


class Vicon_Subject(object):
    def __init__(self, name, folder):
        self.name = name
        self.folder = folder
        self.trails = {}

    def add_trail(self, asc, condition, time, foot, stances):
        # the same trail's information in the same condition and time is seperated in different entries
        # each one contains one foot type with stances timestamp
        # therefore firstly construct the self.trails[condition][time] dictionary construction
        if condition not in self.trails.keys():
            self.trails[condition] = {}
        
        if time not in self.trails[condition].keys():
            self.trails[condition][time] = {}

        # store the asc file object to self.trails[condition][time]['asc']
        asc_object = Vicon_asc('{}/{}/{}.asc'.format(self.folder, self.name, asc))
        self.trails[condition][time]['asc'] = asc_object

        # then filled foot and stances data, which complete the dictionary structure to
        # self.trails[condition][time][foot][stance]
        self.trails[condition][time][foot] = {}
        for stance in stances:
            try:
                start = float(re.search('^[0-9\.]+[^-]', stance).group())
                end = float(re.search('[^-][0-9\.]+$', stance).group())
                self.trails[condition][time][foot][stance] = asc_object.get_time_sensor_slice(
                    foot, start, end,
                )
            except:
                pass


class Trails_Parser(object):
    def __init__(self, path):
        self.doc = pd.read_excel(path)
        folder = re.search('^.*/', path).group()
        folder = re.sub('/', '', folder)
        self.subjects = {}

        length = len(self.doc.index)
        print("loading {} data entries".format(length))
        for index in self.doc.index:
            # parse information of each trail
            asc = self.doc.loc[index, 'Unnamed: 0']
            condition = re.search('[^0-9 ][a-z ]+[^0-9 ]', asc).group()
            time = re.search('[0-9]+$', asc).group()
            foot = self.doc.loc[index, 'sideFoot']
            stances = self.doc.loc[index, 'stance phase 1':]

            # parse the subject's name
            # if the subject hasn't been added to self.subjects dictionary, add it
            subject_name = re.search('^S[0-9]+', asc).group()
            if subject_name not in self.subjects.keys():
                self.subjects[subject_name] = Vicon_Subject(subject_name, folder)
            
            # add a trial to the subject
            self.subjects[subject_name].add_trail(asc, condition, time, foot, stances)
            drawProgressBar((index + 1) / length)


def drawProgressBar(percent, barLen = 20):
    """ percent float from 0 to 1 """
    if percent == 1:
        print('')
    else:
        sys.stdout.write("\r")
        sys.stdout.write("[{:<{}}] {:.0f}%".format("=" * int(barLen * percent), barLen, percent * 100))
        sys.stdout.flush()


if __name__ == "__main__":
    trails = Trails_Parser("subjects/walking plantar pressure time slot.xlsx")
    print(trails.subjects.keys())