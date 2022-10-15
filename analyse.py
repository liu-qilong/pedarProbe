import pandas as pd

import pedar
import save

def sensor_peak(node):
    """ Recursively compute average peak pressure for each sensor among conditions, times, etc. """
    if node.level == 5:
        # when recursion reachs stance level, compute peak pressure for each sensor
        node.sensor_peak = node.df.max()

    elif node.level < 5:
        # when recursion reach levels upper than stance
        # recursively call its branches to compute the branches' peak pressure
        # when recursion returns, average all branches' peak pressure as its peak pressure
        branch_sensor_peak_list = []
        for branch in node.branches():
            sensor_peak(branch)
            branch_sensor_peak_list.append(branch.sensor_peak)
        branch_sensor_peak = pd.concat(branch_sensor_peak_list, axis=1)
        node.sensor_peak = branch_sensor_peak.mean(axis=1)

        if node.level == 2:
            print("{}:\n{}".format(node.name, node.sensor_peak))
    else:
        print("Invalid level")


if __name__ == "__main__":
    condition_list = ['fast walking', 'slow walking', 'normal walking']
    data = pedar.Trails_Parser("subjects/walking plantar pressure time slot.xlsx", condition_list)
    sensor_peak(data.subjects['S5'])