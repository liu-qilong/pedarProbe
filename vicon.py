from operator import index
import pandas as pd


class Vicon_asc(object):
    def __init__(self, path, header=9, index_col=0):
        self.doc = pd.read_csv(path, delimiter='\t', header=header, index_col=index_col)

    def get_lf_time_sensor(self, time, sensor_id):
        return self.doc.loc[time, str(sensor_id)]

    def get_rf_time_sensor(self, time, sensor_id):
        return self.doc.loc[time, str(sensor_id) + '.1']

    def get_lf_time_seq(self, time, start_sensor_id, end_sensor_id):
        return self.doc.loc[time, str(start_sensor_id):str(end_sensor_id)]

    def get_rf_time_seq(self, time, start_sensor_id, end_sensor_id):
        return self.doc.loc[time, str(start_sensor_id) + '.1':str(end_sensor_id) + '.1']
    
    def get_lf_sensor_seq(self, sensor_id, start_time, end_time):
        return self.doc.loc[start_time:end_time, str(sensor_id)]
    
    def get_rf_sensor_seq(self, sensor_id, start_time, end_time):
        return self.doc.loc[start_time:end_time, str(sensor_id) + '.1']

    def get_lf_time_sensor_slice(self, start_time, end_time, start_sensor_id, end_sensor_id):
        return self.doc.loc[start_time:end_time, str(start_sensor_id):str(end_sensor_id)]

    def get_rf_time_sensor_slice(self, start_time, end_time, start_sensor_id, end_sensor_id):
        return self.doc.loc[start_time:end_time, str(start_sensor_id) + '.1':str(end_sensor_id) + '.1']


if __name__ == "__main__":
    path = 'subjects/S4/S4 fast walking 1.asc'
    v = Vicon_asc(path)
    print(v.get_lf_sensor_seq(1, 0.02, 0.05))
    print(v.get_rf_sensor_seq(1, 0.02, 0.06))
    print(v.get_lf_time_seq(0.02, 1, 2))
    print(v.get_lf_time_seq(0.02, 1, 2))
    print(v.get_lf_time_sensor(0.02, 99))
    print(v.get_rf_time_sensor(0.02, 99))
    print(v.get_lf_time_sensor_slice(0.02, 0.04, 1, 2))
    print(v.get_rf_time_sensor_slice(0.02, 0.04, 1, 2))