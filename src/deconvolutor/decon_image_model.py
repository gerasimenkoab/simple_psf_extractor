import numpy as np
from scipy.ndimage import zoom
from ..common.ImageRaw_class import ImageRaw
from ..common.DeconMethods_class import DeconMethods
from ..common.BaseModel_class import BaseModel
from ..common.AuxTkPlot_class import AuxCanvasPlot

import logging
import time

class ImageModel(BaseModel):
    """Image Model class"""

    def __init__(self):
        self.logger = logging.getLogger("__main__." + __name__)
        self.logger.debug("Image Model object created")
        super().__init__()

class PSFModel(BaseModel):
    """PSF Model class"""

    def __init__(self):
        self.logger = logging.getLogger("__main__." + __name__)
        self.logger.debug("PSF Model object created")
        super().__init__()
    # Overrides base method
    def GetVisibleLayerImage(self)->ImageRaw:
        array3D = self.mainImageRaw.GetIntensities()
        return AuxCanvasPlot.FigurePILImagekFrom3DArray(array3D, widthPt=800, heightPt = 2400, dpiIn = 400)

    
class DeconImageModel:
    """Image Deconvolution module"""

    def __init__(self):
        self.logger = logging.getLogger("__main__." + __name__)
        self.logger.info("Decon Image Model object created")

        # self._deconImage = BaseModel()
        # self._deconPsf = BaseModel()
        # self._deconResult = BaseModel()
        self._model = {}
        self._model["Image"] = ImageModel()
        self._model["PSF"] = PSFModel()
        self._model["Result"] = ImageModel()        

        self._iterationNumber = 1
        self._regularizationParameter = 0.00001

    @property
    def deconImage(self):
        return self._model["Image"]

    def SetDeconImage(self, fname=None, voxel=None, array=None):
        self._model["Image"].SetMainImage(fname, voxel, array)

    @property
    def deconPsf(self):
        return self._model["PSF"]

    def SetDeconPsf(self, fname=None, voxel=None, array=None):
        self._model["PSF"].SetMainImage(fname, voxel, array)

    @property
    def deconResult(self):
        return self._model["Result"]


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

    # def _getTargetModel(self, canvasName):
    #     """Auxilary function to get target model by canvas name"""
    #     match canvasName:
    #         case "Image":
    #             target = self._deconImage
    #         case "PSF":
    #             target = self._deconPsf
    #         case "Result":
    #             target = self._deconResult
    #         case _:
    #             self.logger.error("Wrong canvas name: "+canvasName)
    #             raise ValueError("Wrong canvas name", "canvas-name-incorrect")
    #     return target

    def SetVisibleLayerNumberFor(self, canvasName:str = "Image", layerNumber:int = 0 )->None:
        try:
            target = self._model[canvasName]
        except KeyError:
            self.logger.error("Wrong canvas name: "+canvasName)
            raise 
        try:
            target.SetVisibleLayerNumber(layerNumber)
        except ValueError:
            self.logger.error("Wrong layer number: "+str(layerNumber))
            raise

    def GetVisibleLayerNumberFor(self, canvasName:str = "Image")->int:
        try:
            target = self._model[canvasName]
        except KeyError:
            self.logger.error("Wrong canvas name: "+canvasName)
            raise
        return target.GetVisibleLayerNumber()

    def GetInfoStringFor(self,canvasName:str = "Image")->str:
        try:
            target = self._model[canvasName]
        except KeyError:
            self.logger.error("Wrong canvas name: "+canvasName)
            raise
        return target.GetInfoString("full")

    def GetVisibleLayerImageFor(self, canvasName:str = "Image")->ImageRaw:
        try:
            target = self._model[canvasName]
        except KeyError:
            raise
        return target.GetVisibleLayerImage()

    def VisibleLayerChange(self, direction:str, canvasName:str = "Image")->None:
        if direction not in ["up", "down"] :
            raise ValueError("Wrong direction", "direction-incorrect")
        try:
            target = self._model[canvasName]
        except KeyError:
            self.logger.error("Wrong canvas name: "+canvasName)
            raise
        if direction == "up":
            target.VisibleLayerNumberUp()
        else:
            target.VisibleLayerNumberDown()
 
    def DeconvolveImage(self, deconMethodIn: str):
        doRescalePSF = True
        self.logger.debug("step 1: rescale PSF to match image voxel size. "+ str(doRescalePSF))
        image = self._model["Image"].mainImageRaw
        psf = self._model["PSF"].mainImageRaw
        if doRescalePSF:
            rescaleCoefZ = psf.GetVoxelFromAxis("Z") / image.GetVoxelFromAxis("Z") 
            rescaleCoefY = psf.GetVoxelFromAxis("Y") / image.GetVoxelFromAxis("Y") 
            rescaleCoefX = psf.GetVoxelFromAxis("X") / image.GetVoxelFromAxis("X") 
            try:
                kernell = zoom(psf.GetIntensities(),[rescaleCoefZ, rescaleCoefY, rescaleCoefX])
            except (RuntimeError, ValueError, MemoryError) as e:
                self.logger.debug("PSF Rescale failed"+str(e))
                raise RuntimeError("PSF Rescale failed", "psf-rescale-failed")
        self.logger.debug("step 2: deconvolution")
        start_time = time.time()
        try:
            PSFArray = DeconMethods.DeconImage(
                image.GetIntensities(),
                kernell, # psf.GetIntensities(),
                self._iterationNumber,
                deconMethodIn,
                self._regularizationParameter
            )

        except Exception as e:
            self.logger.error("Image Deconvolution failed" + str(e))
            raise
        try:
            self._model["Result"] = BaseModel(ImageRaw( None, list(self._model["Image"].mainImageRaw.GetVoxel()), PSFArray ))
        except ValueError as e:
            self.logger.error("Deconvolution result assign failed" + str(e))
            raise RuntimeError("Deconvolution result assign failed", "deconvolution-result-assign-failed")
        self.logger.info("Deconvolution time: %s seconds " % (time.time() - start_time))
