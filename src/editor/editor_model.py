import numpy as np
import os
from scipy.ndimage import gaussian_filter, median_filter
from common.ImageRaw_class import ImageRaw

import logging


class EditorModel:
    def __init__(self, image: ImageRaw = None):
        # super().__init__
        self.logger = logging.getLogger("__main__." + __name__)
        self.logger.info("Image Editor opened")
        if image is None:
            self._mainImage = ImageRaw(None, [0.2, 0.089, 0.089], np.zeros((10, 200, 200)))
        elif isinstance(image, ImageRaw):
            self._mainImage = image
        else:
            raise ValueError("ImageRaw object expected", "image-type-error")

    @property
    def mainImage(self):
        return self._mainImage

    def SetMainImage(self, fname=None, voxel=None, array=None):
        self._mainImage = ImageRaw(fname, voxel, array)

