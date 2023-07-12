from model.decon_psf_model import DeconPsfModel
from view.decon_psf_view import DeconPsfView
from app_logger import AppLogger
#import loggin
class DeconPsfController(AppLogger):
    def __init__(self) -> None:
        super().__init__()
        #setup logger
        # self.logger = logging.getLogger(__name__)
        # self.handler = RotatingFileHandler("logs/extractor_event.log",maxBytes=6000, backupCount=2)
        # self.handler.setFormatter(logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        # self.handler.setLevel(logging.INFO)
        # self.logger.addHandler(self.handler)
        # self.logger.setLevel(logging.INFO)
        self.logger.info("Initializing Bead Extractor.")

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