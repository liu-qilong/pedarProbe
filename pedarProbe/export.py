import pandas as pd


def export_conditions_attribute(subjects, attr_name, export_folder='output'):
    # retrieve all conditions' sensor peak pressure
    row_name_list = []
    attribute_list = []
    for subject in subjects.branches():
        for condition in subject.branches():
            row_name_list.append("{} {}".format(subject.name, condition.name))
            attribute_list.append(condition.attribute[attr_name])
    
    # rearrange as a data frame and export
    df_condition = pd.DataFrame({"condition": row_name_list})
    df_data = pd.concat(attribute_list, axis=1).transpose()
    df_export = pd.concat([df_condition, df_data], axis=1)

    df_export.to_excel("{}/{}.xlsx".format(export_folder, attr_name))