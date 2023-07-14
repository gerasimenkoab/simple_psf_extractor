import numpy as np
import os
from scipy.ndimage import gaussian_filter, median_filter
from .ImageRaw_class import ImageRaw

import logging







class DeconPsfModel():
    def __init__(self):
        super().__init__
        self.logger = logging.getLogger('__main__.'+__name__)
        self.logger.info("Decon PSF object created")
        self._PSFImage = ImageRaw(None, [0.2, 0.089, 0.089], np.zeros((10, 200, 200)))
        self._beadDiameter = 0.2

    @property
    def PSFImage(self):
        return self._PSFImage

    def SetMainImage(self, fname=None, voxel=None, array=None):
        self._PSFImage = ImageRaw(fname, voxel, array)

    @property
    def beadDiameter(self):
        return self._beadDiameter

    @beadDiameter.setter
    def beadDiameter(self, value):
        if value > 0 and type(value) == int or float:
            self._beadDiameter = value
        else:
            raise ValueError("Wrong bead diameter value", "beadDiameter_incorrect")

    def SetVoxelSize(self, newVoxelSizeList):
        """Bead voxel size change"""
        try:
            self._PSFImage.SetVoxel(newVoxelSizeList)
        except ValueError as vErr:
            raise ValueError(vErr.args)
