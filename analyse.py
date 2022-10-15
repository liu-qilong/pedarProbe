import pandas as pd

def sensor_peak(node):
    """ recursively compute average peak pressure for each sensor among conditions, times, etc. """
    if node.level == 5:
        # when recursion reachs stance level, compute peak pressure for each sensor
        # and store it as node.sensor_peak
        node.sensor_peak = node.df.max()

    elif node.level < 5:
        # when recursion reach levels upper than stance
        # recursively call its branches to compute the branches' peak pressure
        # when recursion returns, average all branches' peak pressure as its node.sensor_peak
        branch_sensor_peak_list = []
        for branch in node.branches():
            sensor_peak(branch)
            branch_sensor_peak_list.append(branch.sensor_peak)
        branch_sensor_peak = pd.concat(branch_sensor_peak_list, axis=1)
        node.sensor_peak = branch_sensor_peak.mean(axis=1)

    else:
        print("Invalid level")