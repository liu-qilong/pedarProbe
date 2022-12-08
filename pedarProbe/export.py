from __future__ import annotations
from typing import Type, Union

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageOps

import node

def export_conditions_attribute(subjects, attr_name, export_folder='output', save_suffix: str = ''):
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

    df_export.to_excel("{}/{}{}.xlsx".format(export_folder, attr_name, save_suffix))


def export_attribute_heatmap(node: Type[node.Node], attr_name: str = 'sensor_peak', is_export: bool = True, mask_dir: str = 'data/left_foot_mask.png', export_folder: str = 'output', save_suffix: str = ''):
    """Convert an attribute of a node to hot map figure and export."""

    # load the left foot mask image
    # flip it as the right foot mask image
    l_mask = Image.open(mask_dir)
    r_mask = ImageOps.mirror(l_mask)

    # detect pixels of area no.1~198 and store the corresponding indexes
    l_pedar = np.array(l_mask).astype(np.float64)
    r_pedar = np.array(r_mask).astype(np.float64)
    l_index = {}
    r_index = {}

    for n in range(0, 199):
        l_index[n] = np.where(l_pedar == n + 1)
        r_index[n + 99] = np.where(r_pedar == n + 1)

    # fill the attribute distribution
    for n in node.attribute[attr_name].index:
        if n <= 99:
            # filling left foot area
            l_pedar[l_index[n]] = node.attribute[attr_name][n]
        else:
            # filling right foot area
            r_pedar[r_index[n]] = node.attribute[attr_name][n]

    # show as heatmap
    plt.imshow(l_pedar, cmap='cool')
    plt.show()

    plt.imshow(r_pedar, cmap='cool')
    plt.show()

    # export as heatmap
    if is_export:
        plt.imshow(l_pedar, cmap='cool')
        plt.savefig('{}/l_heatmap{}'.format(export_folder, save_suffix))

        plt.imshow(r_pedar, cmap='cool')
        plt.savefig('{}/r_heatmap{}'.format(export_folder, save_suffix))