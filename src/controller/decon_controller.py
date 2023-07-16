from model.decon_psf_model import DeconPsfModel
from view.decon_view import DeconView
import logging
class DeconController():
    def __init__(self,master) -> None:
        super().__init__()
        #setup logger
        self.logger = logging.getLogger('__main__.'+__name__)
        self.logger.info("Initializing PSF deconvolution module.")

        self._master = master

        self.model = DeconPsfModel()
        self.view = DeconView( self._master )
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