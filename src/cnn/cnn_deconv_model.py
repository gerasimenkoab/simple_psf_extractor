import numpy as np
from ..common.ImageRaw_class import ImageRaw
from ..cnn.CNN_Deconvolution.DeblurPredictor import DeblurPredictor

import logging


# TODO : Add model from server loading
class CNNDeconvModel:
    """Image Deconvolution module"""

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("__main__." + __name__)
        self.logger.info("Decon Image object created")

        self._deconImage = ImageRaw(None, [0.2, 0.089, 0.089], np.zeros((10, 200, 200)))
        self._deconResult = None

    @property
    def deconImage(self):
        return self._deconImage

    @deconImage.setter
    def deconImage(self, value: ImageRaw):
        self._deconImage = value

    def SetDeconImage(self, fname=None, voxel=None, array=None):
        self._deconImage = ImageRaw(fname, voxel, array)

    @property
    def deconResult(self):
        return self._deconResult

    @deconResult.setter
    def deconResult(self, value: ImageRaw):
        self._deconResult = value

    def SetDeconReslult(self, fname=None, voxel=None, array=None):
        self._deconResult = ImageRaw(fname, voxel, array)

    def DeconvolveImage(self):
        try:
            self.logger.info("In deconv method")
            predictor = DeblurPredictor()

            self.logger.info(f"predictor: {predictor}")

            img_shape = self._deconImage.GetImageShape()
            self.logger.info(f"Image shape: {img_shape}")

            intensities = self._deconImage.GetIntensities()
            intensities = intensities[0:img_shape[0] - img_shape[0] % 8, :, :]
            self.logger.info(f"Intensities shape: {intensities.shape}")
            self._deconImage.SetIntensities(intensities)

            predictor.initPredictModel(img_shape[0], img_shape[1], img_shape[2], "3d deconvolution")
            self.logger.info(f"predictor is inited: {predictor.isInited}")
            if predictor.isInited:
                result_img = predictor.makePrediction(self._deconImage.GetIntensities())
                self.logger.info(f"Prediction made, result image shape: {result_img.shape}")
            else:
                self.logger.error("Predictor initialization failed.")
                result_img = None
            if result_img is not None:
                self._deconResult = ImageRaw(intensitiesIn=result_img, voxelSizeIn=self._deconImage.GetVoxel())
                self.logger.info(f"Result image shape: {self._deconResult.GetImageShape()}")
            else:
                self.logger.error("Deconvolved image is None.")
        except Exception as e:
            self.logger.debug(str(e))
            return
        self.logger.info("CNN deconv completed.")