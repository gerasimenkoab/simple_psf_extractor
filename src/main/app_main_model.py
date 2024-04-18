import logging
from common.ImageRaw_class import ImageRaw
from common.BaseModel_class import BaseModel
from common.DenoiseImage_class import ImageDenoiser

class MainAppModel(BaseModel):
    def __init__(self, image: ImageRaw = None):
        self.logger = logging.getLogger("__main__." + __name__)
        self.logger.info("Image Editor opened")
        BaseModel.__init__(self,image)
        self._denoiser = ImageDenoiser()
        
    def getDnoiseMethodsList(self):
        return self._denoiser.getDnoiseMethodsList()

    def setDenoiseMethod(self, method:str)->None:
        try:
            self._denoiser.setDenoiseMethod(method)
        except ValueError as e:
            self.logger.error("Can't set denoise method. "+str(e))
            raise
            
    def performDenoise(self)->None:
        try:
            self._denoiser.denoise(self._mainImageRaw.GetIntensities())
        except RuntimeError as e:
            self.logger.error("Can't denoise image. "+str(e))
            raise