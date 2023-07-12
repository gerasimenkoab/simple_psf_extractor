import logging
from logging.handlers import RotatingFileHandler


class AppLogger:
    def __init__(self) -> None:
        # self.logger = logging.getLogger(__name__)
        # self.handler = RotatingFileHandler("logs/extractor_event.log",maxBytes=6000, backupCount=2)
        # self.handler.setFormatter(logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        # self.handler.setLevel(logging.INFO)
        # self.logger.addHandler(self.handler)
        # self.logger.setLevel(logging.INFO)

        RotatingFileHandler("logs/extractor_event.log",maxBytes=6000, backupCount=2)
        logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        logging.basicConfig(level=logging.INFO)

