from model.decon_image_model import DeconImageModel
from view.decon_image_view import DeconImageView
import logging

class DeconImageController():
    def __init__(self,master) -> None:
        super().__init__()
        #setup logger
        self.logger = logging.getLogger('__main__.'+__name__)
        self.logger.info("Initializing Image deconvolution module.")

        self._master = master

        self.model = DeconImageModel()
        self.view = DeconImageView( self._master )
        self._beadPrevNum = 0

        self.view.SetVoxelValues(self.model.mainImage.voxel)
        self.view.SetBeadSize(self.model.beadDiameter)
        # binding buttons and entries events                    
        self._bind()


   # TODO : remove clicker test
    def buttonClickTest(self):
        print("clicked")

 
    def _bind(self):
        pass