import logging
import copy
import numpy as np
from common.ImageRaw_class import ImageRaw
# from common.DenoiseImage_class import ImageDenoiser, DenoiseImage

from PIL import Image, ImageEnhance, ImageOps, TiffImagePlugin


class BaseModel:
    def __init__(self, image: ImageRaw = None):
        self.logger = logging.getLogger("__main__." + __name__)
        self.logger.info("Image Editor opened")
        if image is None:
            self._mainImageRaw = ImageRaw( voxelSizeIn=[0.1,0.1,0.1], intensitiesIn=np.zeros((10,10,10)) )
        elif isinstance(image, ImageRaw):
            self._mainImageRaw = image
        else:
            raise ValueError("ImageRaw object expected", "image-type-error")
        self._mainImageRaw.SetIntensities( self.NormalizeImageArray(self._mainImageRaw.GetIntensities()) )

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
            self.logger.error("Can't convert array to list of images. "+str(e))
            raise ValueError("Can't convert array to list of images", "array-conversion-failed")
        
        self.SetVisibleLayerNumber( int((len(self.imgBeadsRawList) + 1) / 2) )
        

    # def getDnoiseMethodsList(self):
    #     return DenoiseImage.getImplementedMethodsList()
    


    # def denoiseImage(self, denoiseType:str)->None:
    #     """Denoise main image by denoise type"""
    #     try:
    #         self._mainImageRaw.SetIntensities( DenoiseImage.denoiseByMethodDefault(self._mainImageRaw.GetIntensities(), denoiseType) )
    #     except Exception as e:
    #         self.logger.error("Can't denoise image. "+str(e))
    #         raise ValueError("Can't denoise image", "image-denoising-failed")
    #     self._ConvertMainImageRawToPILImage()

    def NormalizeImageArray(self, array):
        """Normalize array values to 0-255 range"""
        array = array / np.amax(array) * np.iinfo(np.uint8).max
        return array.astype(np.uint8)

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


    def _ChangeImageColor(self, img:Image, color:str):
        """Change color of image object"""
        #set image to greyscale
        imgGreyScale = img.convert('L')
        if color == "grey":
            return imgGreyScale
        return ImageOps.colorize(imgGreyScale, black="black", white="white", mid = color,
                                 blackpoint=0, whitepoint=255, midpoint=128)

    def _ConvertMainImageRawToPILImage(self):
        """Loading raw beads photo from file"""
        ArrayIn = self._mainImageRaw.GetIntensities()
        if ArrayIn is None:
            raise ValueError("Main image array is None", "array-empty")
        self.imgBeadsRawList = []
        try:
            for i in range(ArrayIn.shape[0]):
                try:
                    tmpArray = ArrayIn[i,:,:].reshape((ArrayIn.shape[1],ArrayIn.shape[2]))
                except Exception as e:
                    self.logger.error("Can't reshape array. "+str(e))
                    raise ValueError("Can't reshape array", "array-reshaping-failed")
                # use .convert('L') when make array from numpyArray to avoid problem with F mode   
                # !caution! fromarray(tmpArray, mode="L") does not work as intended, so use convert('L').
                try:
                    tmp = self._ChangeImageColor(img = Image.fromarray(tmpArray), color = self._mainImageColor)
                except Exception as e:
                    self.logger.error("Can't colorise image. "+str(e))
                    raise ValueError("Can't colorise image", "image-colorising-failed")
                self.imgBeadsRawList.append(tmp)
        except:
            raise ValueError("Can't convert array to Image colorised", "array-to-image-conversion-failed")
        self._visibleLayerNumber = int((len(self.imgBeadsRawList) + 1) / 2)

    def SetBrightnessValue(self, value):
        if value < 0:
            raise ValueError("Brightness value can't be negative", "negative-brightness")
        self._brightnessValue = value

    def SetContrastValue(self, value):
        if value < 0:
            raise ValueError("Contrast value can't be negative", "negative-contrast")
        self._contrastValue = value

    def SetImageColor(self, color:str):
        self._mainImageColor = color
        self._ConvertMainImageRawToPILImage()

    def GetImageColor(self):
        return self._mainImageColor
    
    def CropSelectedArea(self, cropBox:tuple):
        """Crop selected area from image"""
        # crop main image
        x1, y1, x2, y2 = cropBox
        print("cropBox", cropBox)
        # self._mainImageRaw.imArray = self._mainImageRaw.imArray[:, y1:y2, x1:x2]
        self._mainImageRaw.SetIntensities(self._mainImageRaw.GetIntensities()[:, y1:y2, x1:x2])
        self._ConvertMainImageRawToPILImage()
    


    def GetVisibleLayerNumber(self):
        return self._visibleLayerNumber
    
    def SetVisibleLayerNumber(self, number):
        if number < 0 or number >= len(self.imgBeadsRawList):
            raise ValueError("Layer number out of range", "layer-number-out-of-range")
        self._visibleLayerNumber = number
    def GetVisibleLayerArray(self):
        self.mainImageRaw.GetIntensitiesLayer(self.GetVisibleLayerNumber())
        
    def GetVisibleLayerImage(self):
        img = self._AdjustImageLayerBrightnessContrast( self.GetVisibleLayerNumber() )
        return img
    
    def VisibleLayerNumberUp(self):
        self._visibleLayerNumber = (self._visibleLayerNumber + 1) % len(self.imgBeadsRawList)
        return self._visibleLayerNumber
    
    def VisibleLayerNumberDown(self):
        self._visibleLayerNumber = (self._visibleLayerNumber - 1) % len(self.imgBeadsRawList)
        return self._visibleLayerNumber
    
    def GetInfoString(self, option:str = "full"):
        return self._mainImageRaw.GetImageInfoStr(option)

    def SaveImageAsTiff(self, fname:str = "img.tiff", outBitType:str = "L", tagString:str = None):
        """Save Image objects list as multiframe tiff file"""
        images = self._AdjustImageBrightnessContrast()
        images = [img.convert(outBitType) for img in images]
        # Create a TIFF info object and add the custom tag
        info = TiffImagePlugin.ImageFileDirectory_v2()
        if tagString is None:
            info[270] = self._mainImageRaw.GetImageInfoStr("json_voxel")  # 270 is the tag for ImageDescription
        else:
            info[270] = tagString
        try:
            images[0].save(fname, append_images=images[1:], save_all=True, tiffinfo=info)
        except Exception as e:
            self.logger.error("Can't save image as tiff. "+str(e))
            raise ValueError("Can't save image as tiff", "image-saving-failed")
