import logging
from common.ImageRaw_class import ImageRaw
from common.base_model_class import BaseModel

class MainAppModel(BaseModel):
    def __init__(self, image: ImageRaw = None):
        self.logger = logging.getLogger("__main__." + __name__)
        self.logger.info("Image Editor opened")
        super().__init__(image)
