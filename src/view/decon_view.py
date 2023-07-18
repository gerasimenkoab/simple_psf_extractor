from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from tkinter.filedialog import askopenfilenames, askdirectory, asksaveasfilename
from tkinter.simpledialog import askstring
from PIL import ImageTk, Image, ImageEnhance
from .AuxTkPlot_class import AuxCanvasPlot
from view.decon_view_psf import DeconPSFFrameNb
from view.decon_view_image import DeconImageFrameNb
import logging


"""   TODO:
        - fix  AuxTkPlot_class  for all modules
        - add  bead size to tiff tag
"""


class DeconView:
    def __init__(self, master=None):
        # build ui
        self.logger = logging.getLogger('__main__.'+__name__)

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
        self.logger.info("Decon PSF view loaded")



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

    def SetFileInfoImageDeconImage(self, infoStr:str):
        self.deconImageView.imageInfoStr.set(infoStr)

    def SetFileInfoPsfDeconImage(self, infoStr:str):
        self.deconImageView.psfInfoStr.set(infoStr)

    def SetBeadImage(self,arrayIn):
        """Draw canvas with bead image"""
        cnv = self.deconPsfView.canvasBead
        if cnv: 
            cnv.pack_forget() # remove old canvas
        cnvTmp = AuxCanvasPlot.FigureCanvasTkFrom3DArray(arrayIn, self.deconPsfView.deconPSF_plot, plotName="Bead")
        cnvTmp.get_tk_widget().grid(column=0, padx=2, pady=2, row=1)
        pass


    def SetPSFImage(self,arrayIn):
        """Draw canvas with result of deconvolution (PSF)"""
        cnv = self.deconPsfView.canvasPSF
        if cnv: 
            cnv.pack_forget() # remove old canvas
        cnvTmp = AuxCanvasPlot.FigureCanvasTkFrom3DArray(arrayIn, self.deconPsfView.deconPSF_plot, plotName=" ")
        cnvTmp.get_tk_widget().grid(column=1, padx=2, pady=2, row=1)
        pass

    def DrawDeconImage(self,arrayIn):
        """Draw canvas with input image"""
        cnv = self.deconImageView.image_cnv
        imageIn = Image.fromarray(arrayIn)
        # bound ImageTk to out widget - cnv, so set cnv.image. It is done to prevent GC remove image.
        cnv.image = ImageTk.PhotoImage(image = imageIn.resize((350, 350)))
        # replacing image on the canvas
        cnv.create_image((0, 0), image=cnv.image, state = 'normal', anchor=NW)

    def DrawResultImage(self,arrayIn):
        """Draw canvas with input image"""
        cnv = self.deconImageView.result_cnv
        imageIn = Image.fromarray(arrayIn)
        # bound ImageTk to out widget - cnv, so set cnv.image. It is done to prevent GC remove image.
        cnv.image = ImageTk.PhotoImage(image = imageIn.resize((350, 350)), master = cnv)
        # replacing image on the canvas
        cnv.create_image((0, 0), image = cnv.image, state = 'normal', anchor=NW)


    def DrawDeconPsf(self,arrayIn):
        """Draw canvas with result of deconvolution (PSF)"""
        cnv = self.deconImageView.psf_cnv
        if cnv: 
            cnv.pack_forget() # remove old canvas
        cnvTmp = AuxCanvasPlot.FigureCanvasTkFrom3DArray(arrayIn, self.deconImageView.psfFrame, plotName="")
 # fix grid pack       cnvTmp.grid(column=1, padx=2, pady=2, row=1)
        pass

    def GetVoxelDialog(self, widget, textInfo=""):
        """
        Create diealog and return list of values
        """
        voxelStr = askstring(parent = widget, title = "Voxel Dialog", prompt = textInfo)
        try:
            voxelList = [float(a) for a in voxelStr.split(",")]
        except:
            raise ValueError("Can not get voxel values", "bad-voxel-string")
        if voxelStr == "":
            raise ValueError("Can not get voxel values", "bad-voxel-string")
        return voxelList

    def GetFileNamesList(self, widget, titleTxt = ""):
        self.logger.debug("GetFileNamesList called")
        try:
            fNames = askopenfilenames(parent = widget, title = titleTxt)
        except:
            raise ValueError("Can not get file names","no-filenames-read")
        if fNames == "":
            raise ValueError("Can not get file names","no-filenames-read")
        return fNames

    def run(self):
        self.mainwindow.mainloop()

    def callback(self, event=None):
        pass


if __name__ == "__main__":
    app = DeconView()
    app.run()
