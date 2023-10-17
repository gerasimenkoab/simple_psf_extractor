from view.extractor_beadpreview_view import ExtractorBeadPreviewWidget
import logging


class ExtractorBeadPreviewController():
    def __init__(self, master = None, modelIn = None ):
        self.logger = logging.getLogger("__main__." + __name__)
        self.logger.info("Initializing Extractor Bead Preview module.")

        if modelIn is None:
            return
        self._master = master
        self._model = modelIn
        self._view = ExtractorBeadPreviewWidget(self._master)
        # upload bead list

