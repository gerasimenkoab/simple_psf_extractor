from model.decon_psf_model import DeconPsfModel
from view.decon_psf_view import DeconPsfView
from app_logger import AppLogger
import logging
class DeconPsfController(AppLogger):
    def __init__(self,master) -> None:
        super().__init__()
        #setup logger
        self.logger = logging.getLogger('__main__.'+__name__)
        self.logger.info("Initializing PSF deconvolution module.")

        self._master = master

        self.model = DeconPsfModel()
        self.view = DeconPsfView( self._master )
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