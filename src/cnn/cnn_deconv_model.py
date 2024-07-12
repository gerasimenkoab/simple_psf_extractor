import numpy as np
from ..common.ImageRaw_class import ImageRaw
from ..common.BaseModel_class import BaseModel
from ..cnn.CNN_Deconvolution.DeblurPredictor import DeblurPredictor
import logging


class ImageModel(BaseModel):
    """Image Model class"""

    def __init__(self):
        self.logger = logging.getLogger("__main__." + __name__)
        self.logger.debug("Image Model object created")
        super().__init__()


# TODO : Add model from server loading
class CNNDeconvModel:
    """Image Deconvolution module"""

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("__main__." + __name__)
        self.logger.info("Decon Image object created")
        self._model = {}
        self._model["Image"] = ImageModel()
        self._model["Result"] = ImageModel()

        self._deconImage = ImageRaw(None, [0.2, 0.089, 0.089], np.zeros((10, 200, 200)))
        self._deconResult = None

    @property
    def deconImage(self):
        return self._model["Image"]

    @deconImage.setter
    def deconImage(self, value: ImageRaw):
        self._deconImage = value

    def SetDeconImage(self, fname=None, voxel=None, array=None):
        self._deconImage = ImageRaw(fname, voxel, array)

    @property
    def deconResult(self):
        return self._model["Result"]

    def DeconvolveImage(self):
        try:
            print(f"In deconv method")
            predictor = DeblurPredictor()
            
            print(f"predictor: {predictor}")

            # TODO : JUST FOR DEBUG - DELETE THIS ROW LATER
            self._deconImage.imArray = self._deconImage.imArray[0:self._deconImage.imArray.shape[0] - self._deconImage.imArray.shape[0] % 8,:,:]
            predictor.initPredictModel(self._deconImage.imArray.shape[0],
                                            self._deconImage.imArray.shape[1],
                                            self._deconImage.imArray.shape[2],
                                            "3d deconvolution")
            
            print(f"predictor is inited: {predictor.isInited}")
            result_img = predictor.makePrediction(self._deconImage.imArray, None)
            print(f"res: {result_img}")
        except Exception as e:
            self.logger.debug(str(e))
            return
        try:
            self._model["Result"] = BaseModel(
                ImageRaw(None, list(self._model["Image"].mainImageRaw.GetVoxel()), result_img))
        except Exception as e:
            self.logger.debug(str(e))
            return
        self.logger.info("CNN deconv completed.")
