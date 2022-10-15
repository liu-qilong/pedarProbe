import pandas as pd


def export_sensor_peak(subjects, export_folder='result'):
    # retrieve all conditions' sensor peak pressure
    row_name_list = []
    sensor_peak_list = []
    for subject in subjects.branches():
        for condition in subject.branches():
            row_name_list.append("{} {}".format(subject.name, condition.name))
            sensor_peak_list.append(condition.sensor_peak)
    
    # rearrange as a dataframe and export
    df_condition = pd.DataFrame({"condition": row_name_list})
    df_data = pd.concat(sensor_peak_list, axis=1).transpose()
    df_export = pd.concat([df_condition, df_data], axis=1)

    df_export.to_excel("{}/sensor_peak.xlsx".format(export_folder))