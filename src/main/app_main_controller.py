import tkinter as tk
import tkinter.ttk as ttk
from main.app_main_view import MainAppView
from extractor.extractor_controller import ExtractorController
from deconvolutor.decon_controller import DeconController
from cnn.cnn_deconvolution_gui import CNNDeconvGUI
# from cnn.cnn_deconvolution_gui import *
import logging

class MainAppController():
    def __init__(self, master=None):
        self.logger = logging.getLogger('__main__.'+__name__)
        self.logger.info("Main App started.")
        self.MainView = MainAppView( wWidth = 300, wHeight = 250) 

        self._useNNDeconv = False  # set to True if you want to use NN deconvolution

        self._bind()


    def _bind(self):
        """ binding events to the MainView """
        self.MainView.bind("<<RunBeadExtractorWidget>>", lambda event: self.OpenBeadExtractor())
        self.MainView.bind("<<RunDeconvolutionWidget>>", lambda event: self.OpenDeconvolution())
        if self._useNNDeconv:
            self.MainView.bind("<<RunNNDeconvolutionWidget>>", lambda event: self.OpenNNDeconvolution())
        else:
            self.MainView.b3.pack_forget()
        self.MainView.bind("<<ShowAuthors>>", lambda event: self.MainView.ShowAuthors())
        self.MainView.bind("<<CloseApplication>>", lambda event: self.CloseApplication())

    def Run(self):
        self.MainView.mainloop()

    def OpenBeadExtractor(self):
        """Loadding Extractor widget window"""
        ExtractorController(self.MainView)

    def OpenDeconvolution(self):
        """Loadding Deconvolution widget window"""
        DeconController(self.MainView)
    
    def OpenNNDeconvolution(self):
        """Loadding NN deconvolution widget window"""
        if self._useNNDeconv:
            deconvolver = CNNDeconvGUI(self)
        pass

    
    def CloseApplication(self):
        self.MainView.quit()
