from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from PIL import ImageTk, Image, ImageEnhance
from .AuxTkPlot_class import AuxCanvasPlot
from view.decon_view_psf import DeconPSFFrameNb
from view.decon_view_image import DeconImageFrameNb


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
        self.deconNotebook.configure(height=700, width=900)
        self.deconNotebook.pack(expand=True, fill="both", side="top")

        self.deconPsfView = DeconPSFFrameNb(self.deconNotebook)
        self.deconNotebook.add(self.deconPsfView, text = "PSF deconvolution")
        self.deconImageView = DeconImageFrameNb(self.deconNotebook)
        self.deconNotebook.add(self.deconImageView, text = "Image deconvolution")

        self.logOutputLabel = ttk.Label(self.deconPsfToplevel)
        self.logOutStringVar = tk.StringVar(value='Log Output')
        self.logOutputLabel.configure(
            compound="top",
            text='Log Output',
            textvariable=self.logOutStringVar)
        self.logOutputLabel.pack(fill="x", side="bottom")

        # Main widget
        self.mainwindow = self.deconPsfToplevel
    def SetVoxelValues(self, voxelInDict):
        """Bead voxel size change"""
        if voxelInDict is None:
            raise ValueError("No voxel values recived", "voxel_is_none")
        for axisName in ["X","Y","Z"]:
            self.deconPsfView.voxel_entry[axisName].delete(0, END)
            self.deconPsfView.voxel_entry[axisName].insert(0, voxelInDict[axisName])

    def SetBeadSize(self, valueIn):
        """Bead diameter size change"""
        try:
            beadDiameter = abs(float(valueIn))
            self.deconPsfView.beadSize_entry.delete(0, END)
            self.deconPsfView.beadSize_entry.insert(0, str(beadDiameter))
        except:
            showerror("Bead Size: ", "Bad input")
            self.deconPsfView.beadSize_entry.delete(0, END)
            self.deconPsfView.beadSize_entry.insert(0, str(beadDiameter))
            return
    def SetFileInfoDeconPSF(self, infoStr:str):
        self.deconPsfView.loadPsfInfo_entry.configure( state="normal" )
        self.deconPsfView.loadPsfInfo_entry.delete(0,END)
        self.deconPsfView.loadPsfInfo_entry.insert( 0, infoStr )
        self.deconPsfView.loadPsfInfo_entry.configure( state="readonly" )

    def SetBeadImage(self,arrayIn):
        cnv = self.deconPsfView.canvasBead
        if cnv: 
            cnv.pack_forget() # remove old canvas
        cnvTmp = AuxCanvasPlot.FigureCanvasTkFrom3DArray(arrayIn, self.deconPsfView.deconPSF_plot, plotName="Bead")
        cnvTmp.get_tk_widget().grid(column=0, padx=2, pady=2, row=1)
        pass

    def SetPSFImage(self,arrayIn):
        cnv = self.deconPsfView.canvasPSF
        if cnv: 
            cnv.pack_forget() # remove old canvas
        cnvTmp = AuxCanvasPlot.FigureCanvasTkFrom3DArray(arrayIn, self.deconPsfView.deconPSF_plot, plotName="Bead")
        cnvTmp.get_tk_widget().grid(column=1, padx=2, pady=2, row=1)
        pass
    def run(self):
        self.mainwindow.mainloop()

    def callback(self, event=None):
        pass


if __name__ == "__main__":
    app = DeconView()
    app.run()
