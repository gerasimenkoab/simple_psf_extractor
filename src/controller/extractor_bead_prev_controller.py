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
        self._view.SetBeadList(self._model.beadCoords)
        self.ViewBead2D()
        self._bindEvents()

    def _bindEvents(self):
        self._view.deleteBeadBtn.config(command = self.DeleteSelectedBead)
        self._view.previewCloseBtn.config(command=self.CloseBeadPreview)
        self._view.beadsList.bind('<<ListboxSelect>>', self.ViewBead2D)
        self._view.preview3DBtn.config(command=self.ViewBead3D)
    
    def DeleteSelectedBead(self,event= None):
        try:
            id = self._view.beadListViewGet()
        except:
            return
        pass
        self._master.BeadMarksRemoveId(id) 
        self._model.BeadCoordsRemoveId(id)
        self._view.SetBeadList(self._model.beadCoords)
        self.ViewBead2D()   

    def ViewBead2D(self, event=None):
        try:
            id = self._view.beadListViewGet()
        except:
            self._view.PlotBeadPreview2D()
            return
        self._view.PlotBeadPreview2D(self._model._extractedBeads[id].imArray)

    def ViewBead3D(self, event=None):
        try:
            id = self._view.beadListViewGet()
        except:
            return
        self._view.PlotBeadPreview3D(self._model._extractedBeads[id].imArray, '3D Bead plot '+ str(self._model.beadCoords[id]))

    def CloseBeadPreview(self, event=None):
        """Closing window and clear tmp files"""
        self._view.destroy()


