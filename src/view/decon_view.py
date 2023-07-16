from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from PIL import ImageTk, Image, ImageEnhance
#from .AuxTkPlot_class import AuxCanvasPlot
from decon_view_psf import DeconPSFFrameNb
from decon_view_image import DeconImageFrameNb


"""   TODO:
        - fix  AuxTkPlot_class  for all modules
       - add  bead size to tiff tag
"""


class DeconView:
    def __init__(self, master=None):
        # build ui
#        self.logger = logging.getLogger('__main__.'+__name__)
#        self.logger.info("Decon PSF view loaded")

        self.deconPsfToplevel = tk.Tk() if master is None else tk.Toplevel(master)
        self.deconPsfToplevel.configure(
            height=768,
            padx=5,
            pady=5,
            takefocus=True,
            width=1024)
        self.deconPsfToplevel.geometry("950x600")
        self.deconPsfToplevel.maxsize(1920, 1080)
        self.deconPsfToplevel.minsize(950, 600)
        self.deconPsfToplevel.resizable(True, True)
        self.deconPsfToplevel.title("Deconvolution widget")

        self.deconNotebook = ttk.Notebook(self.deconPsfToplevel)
        self.deconNotebook.configure(height=600, width=900)
        self.deconNotebook.pack(expand=True, fill="both", side="top")

        self.deconPsfFrame = DeconPSFFrameNb(self.deconNotebook)
        self.deconNotebook.add(self.deconPsfFrame, text = "PSF deconvolution")
        self.deconImageFrame = DeconImageFrameNb(self.deconNotebook)
        self.deconNotebook.add(self.deconImageFrame, text = "Image deconvolution")

        self.logOutputLabel = ttk.Label(self.deconPsfToplevel)
        self.logOutStringVar = tk.StringVar(value='Log Output')
        self.logOutputLabel.configure(
            compound="top",
            text='Log Output',
            textvariable=self.logOutStringVar)
        self.logOutputLabel.pack(fill="x", side="bottom")
        self.logOutputLabel.bind("<1>", self.callback, add="")

        # Main widget
        self.mainwindow = self.deconPsfToplevel

    def run(self):
        self.mainwindow.mainloop()

    def callback(self, event=None):
        pass


if __name__ == "__main__":
    app = DeconView()
    app.run()
