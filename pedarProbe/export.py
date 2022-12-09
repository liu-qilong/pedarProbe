from __future__ import annotations
from typing import Type, Union

import copy
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


class FootHeatmap(object):
    l_index = None
    r_index = None

    def __init__(self, node: Type[node.Node], attr_name: str = 'sensor_peak', mask_dir: str = 'data/left_foot_mask.png'):
        # if foot mask has never been loaded, call load_foot_mask() method
        if self.l_index is None:
            self.load_foot_mask(mask_dir)

        self.fill_foot_heat_map(node, attr_name)

    @classmethod
    def load_foot_mask(cls, mask_dir: str = 'data/left_foot_mask.png'):
        # load the left foot mask image
        # flip it as the right foot mask image
        l_img = Image.open(mask_dir)
        r_img = ImageOps.mirror(l_img)

        l_mask = np.array(l_img).astype(np.float64)
        r_mask = np.array(r_img).astype(np.float64)

        cls.l_shape = l_mask.shape
        cls.r_shape = r_mask.shape

        # detect pixels of area no.1~198 and store the corresponding indexes
        cls.l_index = {}
        cls.r_index = {}

        for n in range(0, 199):
            cls.l_index[n] = np.where(l_mask == n + 1)
            cls.r_index[n + 99] = np.where(r_mask == n + 1)

    def fill_foot_heat_map(self, node: Type[node.Node], attr_name: str = 'sensor_peak'):
        # create empty left and right distribution
        self.l_pedar = np.zeros(self.l_shape)
        self.r_pedar = np.zeros(self.r_shape)

        # fill the attribute distribution
        for n in node.attribute[attr_name].index:
            if n <= 99:
                # filling left foot area
                self.l_pedar[self.l_index[n]] = node.attribute[attr_name][n]
            else:
                # filling right foot area
                self.r_pedar[self.r_index[n]] = node.attribute[attr_name][n]

    def export_foot_heatmap(self, is_export: bool = True, export_folder: str = 'output', save_suffix: str = ''):
        # calculate value range
        minmin = np.min([np.min(self.l_pedar), np.min(self.r_pedar)])
        maxmax = np.max([np.max(self.l_pedar), np.max(self.r_pedar)])

        # show and export as heatmap
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(7, 8))
        l_img = axes[0].imshow(self.l_pedar, cmap='cool', vmin=minmin, vmax=maxmax)
        r_img = axes[1].imshow(self.r_pedar, cmap='cool', vmin=minmin, vmax=maxmax)

        fig.subplots_adjust(right=0.85)
        cbar_ax = fig.add_axes([0.88, 0.15, 0.04, 0.7])
        fig.colorbar(r_img, cbar_ax)
        plt.show()

        if is_export:
            fig.savefig('{}/foot_heatmap{}'.format(export_folder, save_suffix))

    def __add__(self, other: Type[FootHeatmap]) -> Type[FootHeatmap]:
        new_hm = copy.deepcopy(self)
        new_hm.l_pedar += other.l_pedar
        new_hm.r_pedar += other.r_pedar
        return new_hm

    def __sub__(self, other: Type[FootHeatmap]) -> Type[FootHeatmap]:
        new_hm = copy.deepcopy(self)
        new_hm.l_pedar -= other.l_pedar
        new_hm.r_pedar -= other.r_pedar
        return new_hm

    def __mul__(self, val: Union[float, int]) -> Type[FootHeatmap]:
        new_hm = copy.deepcopy(self)
        new_hm.l_pedar *= val
        new_hm.r_pedar *= val
        return new_hm

    def __truediv__(self, val: Union[float, int]) -> Type[FootHeatmap]:
        new_hm = copy.deepcopy(self)
        new_hm.l_pedar /= val
        new_hm.r_pedar /= val
        return new_hm