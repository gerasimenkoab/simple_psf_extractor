import logging
import copy
import numpy as np
from common.ImageRaw_class import ImageRaw

from PIL import Image, ImageEnhance, ImageOps


class EditorModel:
    def __init__(self, image: ImageRaw = None):
        self.logger = logging.getLogger("__main__." + __name__)
        self.logger.info("Image Editor opened")
        if image is None:
            self._mainImageRaw = ImageRaw(None, [0.2, 0.089, 0.089], np.zeros((10, 200, 200)))
        elif isinstance(image, ImageRaw):
            self._mainImageRaw = image
        else:
            raise ValueError("ImageRaw object expected", "image-type-error")
        self.imgBeadsRawList = [] # list of all tiff frames as  Image objects
        self.imgBeadsRawListStatic = [] # NOT CHANGED list of all tiff frames as  Image objects
        self._mainImageColor = "green"
        try:
            self._ConvertMainImageRawToPILImage()
        except Exception as e:
            self.logger.error("Can't convert raw image to PIL. "+str(e))
            raise ValueError("Can't convert raw image to PIL", "image-conversion-failed")
        self._visibleLayerNumber = int((len(self.imgBeadsRawList) + 1) / 2)

    @property
    def mainImageRaw(self):
        return self._mainImageRaw

    def SetMainImage(self, fname=None, voxel=None, array=None)->None:
        try:
            self._mainImageRaw = ImageRaw(fname, voxel, array)
        except Exception as e:
            self.logger.error("Can't set main image. "+str(e))
            raise ValueError("Can't set main image", "image-setting-failed")

        try:
            self._ConvertMainImageRawToPILImage()
        except Exception as e:
            self.logger.error("Can't convert raw image to PIL. "+str(e))
            raise ValueError("Can't convert raw image to PIL", "image-conversion-failed")
        self._visibleLayerNumber = int((len(self.imgBeadsRawList) + 1) / 2)


    def AdjustImageBrightnessContrast(self, brightnessValue, contrastValue)->None:
        """
        Update Image Layers with  brightness and contrast values.
        """
        for i in range(len(self.imgBeadsRawList)):
            enhancerBrightness = ImageEnhance.Brightness(self.imgBeadsRawListStatic[i])
            imgCanvEnhaced = enhancerBrightness.enhance( brightnessValue )
            enhancerContrast = ImageEnhance.Contrast(imgCanvEnhaced)
            self.imgBeadsRawList[i] = enhancerContrast.enhance( contrastValue )
        
    def SetMainImageColor(self, color:str):
        self._mainImageColor = color

    def _ConvertMainImageRawToPILImage(self):
        """Loading raw beads photo from file"""
        ArrayIn = self._mainImageRaw.imArray
        if ArrayIn is None:
            raise ValueError("Main image array is None", "array-empty")
        try:
            self.imgBeadsRawList=[]
            for i in range(ArrayIn.shape[0]):
                tmpArray = ArrayIn[i,:,:].reshape((ArrayIn.shape[1],ArrayIn.shape[2]))
                # use .convert('L') when make array from numpyArray to avoid problem with F mode   
                # !caution! fromarray(tmpArray, mode="L") does not work as intended, so use convert('L').
                tmp = ImageOps.colorize(Image.fromarray(tmpArray).convert('L'),
                                        black="black",
                                        white="white",
                                        mid = self._mainImageColor)
                self.imgBeadsRawList.append(tmp)
                # ImageOps.colorize(self.imgBeadsRawList[i], black="green", white="white")
        except:
            raise ValueError(
                "Cant set canvas image with beads photo."
            )
        self.imgBeadsRawListStatic = copy.deepcopy(self.imgBeadsRawList)
        self._visibleLayerNumber = int((len(self.imgBeadsRawList) + 1) / 2)


    def GetVisibleLayerNumber(self):
        return self._visibleLayerNumber

    def GetVisibleLayerImage(self):
        return self.imgBeadsRawList[self._visibleLayerNumber]
    
    def VisibleLayerNumberUp(self):
        self._visibleLayerNumber = (self._visibleLayerNumber + 1) % len(self.imgBeadsRawList)
        return self._visibleLayerNumber
    
    def VisibleLayerNumberDown(self):
        self._visibleLayerNumber = (self._visibleLayerNumber - 1) % len(self.imgBeadsRawList)
        return self._visibleLayerNumber
