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

    

