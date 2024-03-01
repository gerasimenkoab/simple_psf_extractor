import numpy as np
import os
from scipy.ndimage import gaussian_filter, median_filter
from .ImageRaw_class import ImageRaw

import logging


class EditorModel:
    def __init__(self):
        super().__init__
        self.logger = logging.getLogger("__main__." + __name__)
        self.logger.info("Image Editor opened")

        self._mainImage = ImageRaw(None, [0.2, 0.089, 0.089], np.zeros((10, 200, 200)))

    @property
    def mainImage(self):
        return self._mainImage

    def SetMainImage(self, fname=None, voxel=None, array=None):
        self._mainImage = ImageRaw(fname, voxel, array)

