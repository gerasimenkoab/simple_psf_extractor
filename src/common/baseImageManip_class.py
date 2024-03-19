import logging
import copy
import numpy as np
from common.ImageRaw_class import ImageRaw

from PIL import Image, ImageEnhance, ImageOps, TiffImagePlugin


class BaseImageManip:
    def __init__(self, image: ImageRaw = None):
        # self.logger = logging.getLogger("__main__." + __name__)
        # self.logger.info("Image Editor opened")
        if image is None:
            self._mainImageRaw = ImageRaw(None, [0.2, 0.089, 0.089], np.zeros((10, 200, 200)))
        elif isinstance(image, ImageRaw):
            self._mainImageRaw = image
        else:
            raise ValueError("ImageRaw object expected", "image-type-error")
        self.imgVisibleLayer = None # visible layer of tiff frames as  Image objects 
        self.imgBeadsRawList = [] # list of all tiff frames as  Image objects
        self.imgBeadsRawListStatic = [] # NOT CHANGED list of all tiff frames as  Image objects
        self._mainImageColor = "green"
        self._visibleLayerNumber = 0
        # Brightness and contrast values
        self._brightnessValue = 1
        self._contrastValue = 1
      
        try:
            self._ConvertMainImageRawToPILImage()
        except Exception as e:
            self.logger.error("Can't convert raw image to PIL. "+str(e))
            raise ValueError("Can't convert raw image to PIL", "image-conversion-failed")
        
        self.SetVisibleLayerNumber( int((len(self.imgBeadsRawList) + 1) / 2) )
        
        

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


    def _AdjustImageBrightnessContrast(self)->None:
        """
        Update Image Layers according to  brightness and contrast values.
        Returns: List of adjusted Image objects.
        """
        imgAdjusted = []
        for imgLayer in range(len(self.imgBeadsRawList)):
            imgAdjusted.append(self._AdjustImageLayerBrightnessContrast(imgLayer))
        return imgAdjusted   

    def _AdjustImageLayerBrightnessContrast(self, layerNum : int)->Image:
        """
        Adjust basic  Image layer number layerNum according to  brightness and contrast values.
        Return: adjusted image as Image object.
        """
        enhancerBrightness = ImageEnhance.Brightness(self.imgBeadsRawList[layerNum])
        imgCanvEnhaced = enhancerBrightness.enhance( self._brightnessValue )
        enhancerContrast = ImageEnhance.Contrast(imgCanvEnhaced)
        return enhancerContrast.enhance( self._contrastValue )


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
        self._visibleLayerNumber = int((len(self.imgBeadsRawList) + 1) / 2)

    def SetBrightnessValue(self, value):
        if value < 0:
            raise ValueError("Brightness value can't be negative", "negative-brightness")
        self._brightnessValue = value

    def SetContrastValue(self, value):
        if value < 0:
            raise ValueError("Contrast value can't be negative", "negative-contrast")
        self._contrastValue = value

    def ChangeImageColor(self, img:Image, color:str):
        """Change color of image object"""
        #set image to greyscale
        
        imgGreyScale = img.convert("L")
        return ImageOps.colorize(imgGreyScale, black="black", white="white", mid = color)
    
    def SetImageColor(self, color:str):
        self._mainImageColor = color
        for i in range(len(self.imgBeadsRawList)):
            self.imgBeadsRawList[i] = self.ChangeImageColor(self.imgBeadsRawList[i], color)

    def GetVisibleLayerNumber(self):
        return self._visibleLayerNumber
    
    def SetVisibleLayerNumber(self, number):
        if number < 0 or number >= len(self.imgBeadsRawList):
            raise ValueError("Layer number out of range", "layer-number-out-of-range")
        self._visibleLayerNumber = number

    def GetVisibleLayerImage(self):
        img = self._AdjustImageLayerBrightnessContrast( self.GetVisibleLayerNumber() )
        return img
    
    def VisibleLayerNumberUp(self):
        self._visibleLayerNumber = (self._visibleLayerNumber + 1) % len(self.imgBeadsRawList)
        return self._visibleLayerNumber
    
    def VisibleLayerNumberDown(self):
        self._visibleLayerNumber = (self._visibleLayerNumber - 1) % len(self.imgBeadsRawList)
        return self._visibleLayerNumber
    

    def SaveImageAsTiff(self, fname:str = "img.tiff", outBitType:str = "L", tagString:str = None):
        """Save Image objects list as multiframe tiff file"""
        images = self._AdjustImageBrightnessContrast()
        images = [img.convert(outBitType) for img in images]
        # Create a TIFF info object and add the custom tag
        info = TiffImagePlugin.ImageFileDirectory_v2()
        if tagString is None:
            info[270] = self._mainImageRaw.GetImageInfoStr()  # 270 is the tag for ImageDescription
        else:
            info[270] = tagString
        try:
            images[0].save(fname, append_images=images[1:], save_all=True, tiffinfo=info)
        except Exception as e:
            self.logger.error("Can't save image as tiff. "+str(e))
            raise ValueError("Can't save image as tiff", "image-saving-failed")
