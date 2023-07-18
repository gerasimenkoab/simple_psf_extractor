import numpy as np
import os
from scipy.ndimage import gaussian_filter, median_filter
from .ImageRaw_class import ImageRaw

import logging

class DeconImageModel():
    """Image Deconvolution module"""
    def __init__(self):
        super().__init__
        self.logger = logging.getLogger('__main__.'+__name__)
        self.logger.info("Decon Image object created")

        self._deconImage = ImageRaw(None, [0.2, 0.089, 0.089], np.zeros((10, 200, 200)))
        self._deconPsf = ImageRaw(None, [0.2, 0.089, 0.089], np.zeros((10, 200, 200)))
        self._deconResult = ImageRaw( None, [0.2, 0.089, 0.089], np.zeros((10, 200, 200)) )

    @property
    def deconImage(self):
        return self._deconImage

    def SetDeconImage(self, fname=None, voxel=None, array=None):
        self._deconImage = ImageRaw(fname, voxel, array)

    @property
    def deconPsf(self):
        return self._deconPsf

    def SetDeconPsf(self, fname=None, voxel=None, array=None):
        self._deconPsf = ImageRaw(fname, voxel, array)

    @property
    def deconResult(self):
        return self._deconResult


