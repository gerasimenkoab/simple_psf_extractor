import copy
import logging
import os

import numpy as np

from ..CNN_Deconvolution.BigImageManager import BigImageManager
from ..CNN_Deconvolution.DeblurCNNModel2D import DeblurCNNModel2D
from ..CNN_Deconvolution.DeblurCNNModelMini3D import DeblurCNNModelMini3D


# Class, which provides predicting of output data
class DeblurPredictor:
    # constructor
    def __init__(self):
        # CONSTANTS
        self.CHUNK_SIZE = 64
        self.OFFSET_SIZE = 32
        self.CNN_MODEL_PATH_3D = "./web/backend/engine/src/cnn/CNN_Deconvolution/models/3d_gaus_blur.h5"
        self.CNN_MODEL_PATH_2D = "./web/backend/engine/src/cnn/CNN_Deconvolution/models/2d_gaus_blur.h5"

        self.isInited = False
        self.currentType = None
        self.logger = logging.getLogger("__main__." + __name__)
        self.model = None

    def initPredictModel(self, layers, rows, cols, type):
        self.currentType = type
        try:
            if type == "3d deconvolution":
                if not os.path.exists(self.CNN_MODEL_PATH_3D):
                    raise FileNotFoundError(f"Model file not found: {self.CNN_MODEL_PATH_3D}")
                _layers = layers
                _rows = self.CHUNK_SIZE + 2 * self.OFFSET_SIZE
                _cols = self.CHUNK_SIZE + 2 * self.OFFSET_SIZE

                self.model = DeblurCNNModelMini3D.ModelBuilder(
                    input_shape=(_layers, _rows, _cols, 1)
                )
                self.model.load_weights(self.CNN_MODEL_PATH_3D)
                self.isInited = True
            elif type == "2d stack deconvolution":
                self.model = DeblurCNNModel2D.ModelBuilder(input_shape=(rows, cols, 1))
                self.model.load_weights(self.CNN_MODEL_PATH_2D)
                self.isInited = True
            else:
                raise Exception("Unknown deconvolution type")
            self.logger.info(f"Model initialized for {type}")
        except Exception as e:
            self.logger.error(f"Failed to initialize model: {str(e)}")
            self.isInited = False

    def makePostprocessing(self, result):
        result = result / np.amax(result)
        return result

    def make2dStackPrediction(self, imgToPredict):
        try:
            layers = imgToPredict.shape[0]
            rows = imgToPredict.shape[1]
            cols = imgToPredict.shape[2]

            imgLayers = [imgToPredict[i] for i in range(layers)]
            resLayers = [self.model.predict(layer.reshape(1, rows, cols, 1)).reshape(rows, cols) for layer in imgLayers]

            predictedImage = np.zeros(shape=(layers, rows, cols), dtype=np.float32)
            for i in range(len(resLayers)):
                predictedImage[i, :, :] = resLayers[i][:, :]
            return predictedImage
        except Exception as e:
            self.logger.error(f"Exception during 2D stack prediction: {str(e)}")
            return None

    def make3dPrediction(self, imgToPredict):
        try:
            chunksMaker = BigImageManager(imgToPredict, self.CHUNK_SIZE, self.OFFSET_SIZE)
            chunks = chunksMaker.SeparateInChunks()

            results = []
            for chunk in chunks:
                chunkToPredict = chunk.chunkData.reshape(
                    1, chunk.dataLayers, chunk.dataRows, chunk.dataCols, 1
                )
                chunkToPredict = self.model.predict(chunkToPredict).reshape(
                    chunk.dataLayers, chunk.dataRows, chunk.dataCols
                )
                chunk.chunkData = chunkToPredict
                results.append(chunk)

            result = chunksMaker.ConcatenateChunksIntoImage(results)
            return result
        except Exception as e:
            self.logger.error(f"Exception during 3D prediction: {str(e)}")
            return None

    def makePrediction(self, img):
        if not self.isInited:
            raise Exception("Model isn't initialized!")

        img = img.astype("float32") / 255
        imgToPredict = img.copy()

        try:
            if self.currentType == "3d deconvolution":
                result = self.make3dPrediction(imgToPredict)
            elif self.currentType == "2d stack deconvolution":
                result = self.make2dStackPrediction(imgToPredict)
            else:
                raise Exception("Unknown prediction type")

            result = self.makePostprocessing(result)
            result = (result * 255).astype("uint8")
            return result
        except Exception as e:
            self.logger.error(f"Exception during prediction: {str(e)}")
            return None
