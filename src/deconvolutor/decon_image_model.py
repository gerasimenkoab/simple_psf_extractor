import numpy as np
from scipy.ndimage import zoom
from common.ImageRaw_class import ImageRaw
from .decon_methods import DeconMethods
from common.BaseModel_class import BaseModel

import logging
import time

class DeconImageModel:
    """Image Deconvolution module"""

    def __init__(self):
        self.logger = logging.getLogger("__main__." + __name__)
        self.logger.info("Decon Image Model object created")

        # self._deconImage = ImageRaw(None, [0.2, 0.089, 0.089], np.zeros((10, 200, 200)))
        # self._deconPsf = ImageRaw(None, [0.2, 0.089, 0.089], np.zeros((10, 200, 200)))
        # self._deconResult = ( None  # ImageRaw( None, [0.2, 0.089, 0.089], np.zeros((10, 200, 200)) )
        self._deconImage = BaseModel()
        self._deconPsf = BaseModel()
        self._deconResult = BaseModel()
        

        self._iterationNumber = 1
        self._regularizationParameter = 0.00001

    @property
    def deconImage(self):
        return self._deconImage

    @deconImage.setter
    def deconImage(self, value: ImageRaw):
        self._deconImage = value

    def SetDeconImage(self, fname=None, voxel=None, array=None):
        self._deconImage.SetMainImage(fname, voxel, array)

    @property
    def deconPsf(self):
        return self._deconPsf

    def SetDeconPsf(self, fname=None, voxel=None, array=None):
        self._deconPsf.SetMainImage(fname, voxel, array)

    @property
    def deconResult(self):
        return self._deconResult

    @deconResult.setter
    def deconResult(self, value: ImageRaw):
        self._deconResult = BaseModel(value)

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

    def _getTargetModel(self, canvasName):
        """Auxilary function to get target model by canvas name"""
        match canvasName:
            case "Image":
                target = self._deconImage
            case "PSF":
                target = self._deconPsf
            case "Result":
                target = self._deconResult
            case _:
                self.logger.error("Wrong canvas name: "+canvasName)
                raise ValueError("Wrong canvas name", "canvas-name-incorrect")
        return target

    def SetVisibleLayerNumberFor(self, canvasName:str = "Image", layerNumber:int = 0 )->None:
        try:
            target = self._getTargetModel(canvasName)
        except:
            raise
        try:
            target.SetVisibleLayerNumber(layerNumber)
        except:
            raise

    def GetVisibleLayerNumberFor(self, canvasName:str = "Image")->int:
        try:
            target = self._getTargetModel(canvasName)
        except:
            raise
        try:
            return target.GetVisibleLayerNumber()
        except:
            raise

    def GetInfoStringFor(self,canvasName:str = "Image")->str:
        try:
            target = self._getTargetModel(canvasName)
        except:
            raise
        try:
            return target.GetInfoString("full")
        except:
            raise

    def GetVisibleLayerImageFor(self, canvasName:str = "Image")->ImageRaw:
        try:
            target = self._getTargetModel(canvasName)
        except:
            raise
        try:
            return target.GetVisibleLayerImage()
        except:
            raise

    def VisibleLayerChange(self, direction:str, canvasName:str = "Image")->None:
        if direction not in ["up", "down"] :
            raise ValueError("Wrong direction", "direction-incorrect")
        target = self._getTargetModel(canvasName)
        if direction == "up":
            target.VisibleLayerNumberUp()
            print("up "+canvasName)
        else:
            target.VisibleLayerNumberDown()
            print("down "+canvasName)

    def DeconvolveImage(self, deconMethodIn: str, progBarIn, masterWidget):
        doRescalePSF = True
        self.logger.debug("step 1: rescale PSF to match image voxel size. "+ str(doRescalePSF))
        image = self._deconImage.mainImageRaw
        psf = self._deconPsf.mainImageRaw
        if doRescalePSF:
            rescaleCoefZ = psf.GetVoxelFromAxis("Z") / image.GetVoxelFromAxis("Z") 
            rescaleCoefY = psf.GetVoxelFromAxis("Y") / image.GetVoxelFromAxis("Y") 
            rescaleCoefX = psf.GetVoxelFromAxis("X") / image.GetVoxelFromAxis("X") 
            try:
                kernell = zoom(psf.GetIntensities(),[rescaleCoefZ, rescaleCoefY, rescaleCoefX])
                # self.imagePSF.RescaleZ(self.img.voxelSize[1])
            except Exception as e:
                self.logger.debug("rescale failed"+str(e))
                raise
        self.logger.debug("step 2: deconvolution")
        start_time = time.time()
        try:
            PSF = DeconMethods.DeconImage(
                image.GetIntensities(),
                kernell, # psf.GetIntensities(),
                self._iterationNumber,
                deconMethodIn,
                self._regularizationParameter,
                progBar=progBarIn,
                parentWin=masterWidget,
            )

        except Exception as e:
            print("Deconvolution failed" + str(e))
            self.logger.debug(str(e))
            raise
        try:
            self._deconResult = BaseModel(ImageRaw( None, list(self._deconImage.mainImageRaw.GetVoxel()), PSF ))
        except Exception as e:
            print("Deconvolution result save failed" + str(e))
            self.logger.debug(str(e))
            raise
        self.logger.info("Deconvolution time: %s seconds " % (time.time() - start_time))
