from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askopenfilenames, asksaveasfilename
from tkinter.simpledialog import askstring
import logging
from typing import Dict, List, Tuple
from PIL import Image, ImageTk


try:
    from ..common.AuxTkPlot_class import AuxCanvasPlot as CnvPlot
except ImportError:
    from common.AuxTkPlot_class import AuxCanvasPlot as CnvPlot

from deconvolutor.decon_view_psf import DeconvolvePSFFrame
from deconvolutor.decon_view_image import DeconvolveImageFrame



# ======= Deconvolution View Class ====================


class DeconView(tk.Toplevel):
    def __init__(self, master=None, wwidth=950, wheight=600):
        self.logger = logging.getLogger('__main__.'+__name__)
        super().__init__(master)
        self.widgets: Dict[str, tk.Widget] = {}
        self.imgCnv: Dict[str,tk.Image] = {}
        self.sourceCanvasImage: Dict[str, tk.Image] = {}

        self.geometry(str(wwidth)+"x"+str(wheight))
        # self.maxsize(1920, 1080)
        self.minsize(wheight, wheight)
        self.resizable(True, True)
        self.title("Deconvolution widget")
        
        # setting up tabs for PSF and Image deconvolution
        self.deconNotebook = ttk.Notebook(self)
        # self.deconNotebook.configure(height=700, width=900)
        self.deconNotebook.pack(expand=True, fill="both", side="top")

        self.deconPsfView = DeconvolvePSFFrame(self.deconNotebook)
        self.deconNotebook.add(self.deconPsfView, text = "PSF deconvolution")

        self.deconImageView = DeconvolveImageFrame(master = self.deconNotebook, widgets = self.widgets)
        self.deconNotebook.add(self.deconImageView, text = "Image deconvolution")

        self.logWidget = ScrolledText(self, wrap = tk.WORD, height = 2)
        self.logWidget.configure(state = "disabled")
        self.logWidget.pack(fill="x", side = "bottom",padx=2, pady=2)

        # binding events for canvas resize
        self.widgets["ImageCanvas"].bind("<Configure>", self.onCanvasSizeChange)
        self.widgets["PSFCanvas"].bind("<Configure>", self.onCanvasSizeChange)
        self.widgets["ResultCanvas"].bind("<Configure>", self.onCanvasSizeChange)

        self.logger.info("Decon widget created")
        # focus on the widget
        self.update_idletasks()
        self.lift()
        

# ======= Auxilary Functions ==========================
    def GetLogWidget(self):
        return self.logWidget

    def SetLogOutput(self, logStr:str):
        self.logger.info(logStr)

    def SetValueWidgetNormal(self, widget, value):
        widget.delete(0, END)
        widget.insert(0, str(value))

    def SetValueWidgetReadonly(self, widget, infoStr):
        widget.configure( state = "normal" )
        widget.delete(0,END)
        widget.insert( 0, infoStr )
        widget.configure( state = "readonly" )

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
            fNames = askopenfilenames(parent = widget, title = titleTxt,
                                      defaultextension=".tiff", 
                                      filetypes=[("TIFF files", "*.tif?")])
        except:
            raise ValueError("Can not get file names","no-filenames-read")
        if fNames == "":
            raise ValueError("Can not get file names","no-filenames-read")
        return fNames

    def GetFileName(self, widget, titleTxt = ""):
        self.logger.debug("GetSaveAsFileName called")
        try:
            fName = asksaveasfilename(parent = widget, 
                                      title = titleTxt,defaultextension=".tiff", 
                                      filetypes=[("TIFF files", "*.tif?")] )
        except:
            raise ValueError("Can not get file names","no-filenames-read")
        if fName == "":
            raise ValueError("Can not get file names","no-filenames-read")
        return fName

    def bindWidget(self, widgetName, event:tk.Event, func:callable)->None:
        try:
            self.widgets[widgetName].bind(event, func)
        except KeyError:
            raise ValueError("No such widget", "no-widget")
# ======= PSF deconvolution Widget Functions ===========
    

    def SetVoxelValues(self, voxelInDict:dict):
        """Bead voxel size change"""
        if voxelInDict is None:
            raise ValueError("No voxel values recived", "voxel_is_none")
        for axisName in ["X","Y","Z"]:
            self.SetValueWidgetNormal(self.deconPsfView.voxel_entry[axisName], voxelInDict[axisName])

    def SetBeadSize(self, valueIn):
        """Bead diameter size change"""
        try:
            self.SetValueWidgetNormal(self.deconPsfView.beadSize_entry, abs(float(valueIn)))
        except:
            self.logger.info("Bead Size: Bad input")
            self.SetValueWidgetNormal(self.deconPsfView.beadSize_entry, self.deconPsfView.beadSize_entry.get())

    def SetFileInfoDeconPSF(self, infoStr:str):
        self.SetValueWidgetReadonly( self.deconPsfView.loadPsfInfo_entry, infoStr)

    def SetBeadImage(self,arrayIn):
        """Draw canvas with bead image"""
        cnv = self.deconPsfView.canvasBead
        if cnv: 
            cnv.pack_forget() # remove old canvas
        #cnvTmp = CnvPlot.FigureCanvasTkFrom3DArray(arrayIn, self.deconPsfView.deconPSF_plot, plotName="Bead")
        cnvTmp = CnvPlot.FigureCanvasTkFrom3DArray(arrayIn, cnv, "Bead",250,450)
        cnvTmp.get_tk_widget().grid(column=0, padx=2, pady=2, row=1)

    def SetPSFImage(self,arrayIn):
        """Draw canvas with result of deconvolution (PSF)"""
        cnv = self.deconPsfView.canvasPSF
        if cnv: 
            cnv.pack_forget() # remove old canvas
        # cnvTmp = CnvPlot.FigureCanvasTkFrom3DArray(arrayIn, self.deconPsfView.deconPSF_plot, plotName=" ")
        cnvTmp = CnvPlot.FigureCanvasTkFrom3DArray(arrayIn, cnv, "PSF",250,450)
        cnvTmp.get_tk_widget().grid(column=1, padx=2, pady=2, row=1)

    def GetPsfDeconMethod(self):
        return self.deconPsfView._deconMethodsDict[self.deconPsfView.deconMethod.get()]

    def GetPsfDeconProgressbar(self):
        return self.deconPsfView.deconPSF_pgbar
    
# ======= Image deconvolution Widget Functions ===========

    def SetFileInfoImageDeconImage(self, infoStr:str):
        self.widgets["ImageInfoStringVar"].set(infoStr)
        self.deconImageView.update()
       
    def SetFileInfoPsfDeconImage(self, infoStr:str):
        self.widgets["PSFInfoStringVar"].set(infoStr)


    # def DrawDeconImage(self,arrayIn):
    #     """Draw input image for deconvolution."""
    #     CnvPlot.Draw2DArrayOnCanvasPIL(arrayIn, self.widgets["ImageCanvas"])

    # def DrawResultImage(self,arrayIn):
    #     """Draw deconvolution result image"""
    #     CnvPlot.Draw2DArrayOnCanvasPIL(arrayIn, self.widgets["ResultCanvas"])

    def DrawImageOnCanvas(self, canvasName:str = "Image", img:Image = None):
        """Draw image on canvas"""
        self.sourceCanvasImage[canvasName] = img
        if img is None:
            return
        _imageScaleFactor = 1.0 # no use for now
        canvas = self.widgets[canvasName+"Canvas"]
        canvas.delete("all")
        self._img_width, self._img_height = img.size

        if self._img_width > self._img_height:
            aspect_ratio = self._img_height / self._img_width
            canvas_height = int(canvas.winfo_height() * _imageScaleFactor)
            # Calculate the new height while keeping the aspect ratio constant
            canvas_width = int(canvas_height / aspect_ratio)
        else:
            aspect_ratio = self._img_width / self._img_height
            canvas_width = int(canvas.winfo_width() * _imageScaleFactor)
            canvas_height = int(canvas_width / aspect_ratio)

        # Resize the image to the size of the canvas
        imgResized = img.resize((canvas_width, canvas_height))
        self.imgCnv[canvasName] = ImageTk.PhotoImage(image=imgResized, master=canvas)
        canvas.create_image((0, 0), image=self.imgCnv[canvasName], state="normal", anchor=NW)
        # updating scrollers
        canvas.configure(scrollregion = canvas.bbox("all"))


    def onCanvasSizeChange(self, event):
        """Resize image on canvas"""
        if len(self.sourceCanvasImage) == 0:
            return
        for canvasName in self.sourceCanvasImage.keys():
            self.DrawImageOnCanvas(canvasName, self.sourceCanvasImage[canvasName])
 

    def GetImageDeconMethod(self):
        return self.widgets["ResultMethodStringVar"].get()
    
    def GetImageDeconIterationNumber(self):
        return int(self.widgets["ResultIterationEntry"].get())

    def GetImageDeconRegularisation(self):
        return int(self.widgets["ResultRegularisationEntry"].get())
    
    def SetImageDeconIterationNumber(self,value):
        try:
            value = int(value)
        except:
            raise ValueError("Wrong iteration number value", "value-not-int")
        if value <= 0:
            raise ValueError("Wrong iteration number value", "value-negative")
        self.SetValueWidgetNormal(self.widgets["ResultIterationEntry"], value)

    def SetImageDeconRegularisation(self,value):
        try:
            value = float(value)
        except:
            raise ValueError("Wrong iteration number value", "value-not-float")
        if 0 < value < 1:
            self.SetValueWidgetNormal(self.widgets["ResultRegularisationEntry"], value)
        else:
            raise ValueError("Wrong iteration number value", "not-allowed-value")

    def GetDeconImageProgressbar(self):
        return self.widgets["ResultProgressBar"]

    def GetImageDeconMethod(self):
        return self.deconImageView._deconMethodsDict[self.widgets["ResultMethodStringVar"].get()]
    



if __name__ == "__main__":
    DeconView(tk.Tk()).mainloop()


    

