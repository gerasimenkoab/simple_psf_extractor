import logging
class BaseModel:
    def __init__(self, controller) -> None:
        self.logger = logging.getLogger("__main__." + __name__)
        self.controller = controller
        self.logger.info("Model created")
        pass

    def modelMethod(self):
        self.logger.info("Model method called")
        pass