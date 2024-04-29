# from common.base_model import BaseModel
from common.Extention_package_base_classes import BaseModel
class Model(BaseModel):
    def __init__(self, controller) -> None:
        super().__init__(controller)

    def processNumber(self, number):
        if not isinstance(number, (int,float)):
            raise ValueError("Invalid number. Please enter a valid number.")
        self.logger.info("Processing number")
        return number * number
