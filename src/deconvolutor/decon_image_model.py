import numpy as np
from scipy.ndimage import zoom
from common.ImageRaw_class import ImageRaw
from .decon_methods import DeconMethods

import logging
import time

class DeconImageModel:
    """Image Deconvolution module"""

    def __init__(self):
        # super().__init__
        self.logger = logging.getLogger("__main__." + __name__)
        self.logger.info("Decon Image Model object created")

        self._deconImage = ImageRaw(None, [0.2, 0.089, 0.089], np.zeros((10, 200, 200)))
        self._deconPsf = ImageRaw(None, [0.2, 0.089, 0.089], np.zeros((10, 200, 200)))
        self._deconResult = ( None  # ImageRaw( None, [0.2, 0.089, 0.089], np.zeros((10, 200, 200)) )
        )

        self._iterationNumber = 1
        self._regularizationParameter = 0.00001

    @property
    def deconImage(self):
        return self._deconImage

    @deconImage.setter
    def deconImage(self, value: ImageRaw):
        self._deconImage = value

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

    @deconResult.setter
    def deconResult(self, value: ImageRaw):
        self._deconResult = value

    @property
    def iterationNumber(self):
        return self._iterationNumber

    @iterationNumber.setter
    def iterationNumber(self, value):
        try:
            value = int(value)
        except:
            raise ValueError("Wrong iteration number", "iteration-number-incorrect")
        if value > 0:
            self._iterationNumber = value
        else:
            raise ValueError("Wrong iteration number", "iteration-number-incorrect")

    @property
    def regularizationParameter(self):
        return self._regularizationParameter

    @regularizationParameter.setter
    def regularizationParameter(self, value):
        try:
            value = float(value)
        except:
            raise ValueError(
                "Wrong regularisation parameter value",
                "regularization-parameter-incorrect",
            )
        if value < 1 and value > 0:
            self._regularizationParameter = value
        else:
            raise ValueError(
                "Wrong regularisation parameter value",
                "regularization-parameter-incorrect",
            )

    def DeconvolveImage(self, deconMethodIn: str, progBarIn, masterWidget):
        doRescalePSF = True
        self.logger.debug("step 1: rescale PSF to match image voxel size. "+ str(doRescalePSF))
        if doRescalePSF:
            rescaleCoefZ = self._deconPsf.GetVoxelFromAxis("Z") / self._deconImage.GetVoxelFromAxis("Z") 
            rescaleCoefY = self._deconPsf.GetVoxelFromAxis("Y") / self._deconImage.GetVoxelFromAxis("Y") 
            rescaleCoefX = self._deconPsf.GetVoxelFromAxis("X") / self._deconImage.GetVoxelFromAxis("X") 
            try:
                kernell = zoom(self._deconPsf.GetIntensities(),[rescaleCoefZ, rescaleCoefY, rescaleCoefX])
                # self.imagePSF.RescaleZ(self.img.voxelSize[1])
            except Exception as e:
                self.logger.debug("rescale failed"+str(e))
                return
        self.logger.debug("step 2: deconvolution")
        start_time = time.time()
        try:
            PSF = DeconMethods.DeconImage(
                self._deconImage.GetIntensities(),
                self._deconPsf.GetIntensities(),
                self._iterationNumber,
                deconMethodIn,
                self._regularizationParameter,
                progBar=progBarIn,
                parentWin=masterWidget,
            )

        except Exception as e:
            print("Deconvolution failed" + str(e))
            self.logger.debug(str(e))
            return
        try:
            self._deconResult = ImageRaw(
                None, list(self._deconImage.GetVoxel()), PSF
            )
        except Exception as e:
            print("Deconvolution result save failed" + str(e))
            self.logger.debug(str(e))
            return
        self.logger.info("Deconvolution time: %s seconds " % (time.time() - start_time))
