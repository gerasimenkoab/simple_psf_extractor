import numpy as np
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from PIL import ImageTk, Image, ImageEnhance, ImageOps

import ctypes

try:
    from .AuxTkPlot_class import AuxCanvasPlot
except:
    from AuxTkPlot_class import AuxCanvasPlot

"""   TODO:
        - fix  AuxTkPlot_class  for all modules
       - add  bead size to tiff tag
"""


class EditorView(tk.Toplevel):
    """Class provides instruments for extraction of beads from microscope multilayer photo."""

    def __init__(self, parent, wwidth=600, wheight=600):
        super().__init__(parent)
        self.beadsPhotoLayerID = 0  # default index of beads microscope photo
        self.imgBeadsRaw = None
        self.brightnessValue = 1
        self.contrastValue = 1
        self.mainImageColor = "green" #"red"

        self.xr = 0
        self.yr = 0
        self.button_name = {
            "Close": "Close Extractor",
        }
        self.button_dict = {}  # according to list of names {id_name : widget}
        self.entry_dict = {}  # according to list of names {id_name : widget}
        self.label_dict = {}  # label {id_name : string}
        # new window widgets
        self.title("Image Editor")
        self.resizable(False, False)

        # ----------------------------- Menu Bar ----------------------------
        self.menubar = Menu(self)
        filemenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=filemenu)
        # filemenu.add_command(
        #     label="Load Image",
        #     underline=0,
        #     accelerator="Ctrl+o",
        #     command=lambda: self.event_generate("<<LoadImage>>"),
        # )
        filemenu.add_command(
            label="Save Image",
            underline=1,
            command=lambda: self.event_generate("<<SaveImageInEditor>>"),
        )
        filemenu.add_separator()
        filemenu.add_command( label="Close", comman=lambda: self.event_generate("<<CloseEditor>>") )
        self.config(menu=self.menubar)

        # --------------------------- End Menu Bar ------------------------------


        # -------------- image and canvas frame --------------------------

        parametersFrame = Frame(self)
        imageParamFrame = Frame(parametersFrame)
        ttk.Label(
            imageParamFrame,
            text="Image",
            font="Helvetica 10 bold",
        ).grid(row=0, column=0, sticky="n")

        self.imageInfoStr = tk.StringVar(value="No Image Loaded")
        self.imageInfo_lbl = ttk.Label(imageParamFrame, textvariable=self.imageInfoStr)
        self.imageInfo_lbl.grid(row=1, column=0, sticky="n")

        tiffTypeSelectFrame = Frame(imageParamFrame)
        self.tiffMenuBitText = ["8 bit", "16 bit", "32 bit"]
        self.tiffMenuBitDict = {
            "8 bit": "uint8",
            "16 bit": "uint16",
            "32 bit": "uint32",
        }
        self.tiffSaveBitType = StringVar()
        self.tiffSaveBitType.set(self.tiffMenuBitText[0])
        ttk.Label(tiffTypeSelectFrame, width=10, text="Tiff type ").pack(
            side=LEFT, padx=2, pady=2
        )
        self.tiffType_menu = ttk.OptionMenu(
            tiffTypeSelectFrame, self.tiffSaveBitType, *self.tiffMenuBitText
        )
        self.tiffType_menu.pack(side=LEFT, padx=2, pady=2)
        tiffTypeSelectFrame.grid(row=2, column=0, sticky="n")

        brightnessFrame = Frame(imageParamFrame)
        ttk.Label(brightnessFrame, text="Brightness").pack(side=tk.TOP, padx=2, pady=2)
        self.brightnessScaleVar = DoubleVar()
        self.brightnessScale = ttk.Scale(brightnessFrame, orient='horizontal', from_=-8, to_=8,
                                         variable = self.brightnessScaleVar)
        self.brightnessScale.set(1)
        self.brightnessScale.configure( command= self.AdjustBrightness )
        self.brightnessScale.pack(side=tk.TOP)
        ttk.Label(brightnessFrame, text="Contrast").pack(side=tk.TOP, padx=2, pady=2)
        self.contrastScale = ttk.Scale(brightnessFrame, orient='horizontal', from_=-8, to_=8)
        self.contrastScale.set(1)
        self.contrastScale.configure( command= self.AdjustContrast )
        self.contrastScale.pack(side=tk.TOP)

        brightnessFrame.grid(row=3, column=0, sticky="n")


        layerFrame = Frame(imageParamFrame)

        ttk.Label(layerFrame, text=" Layer:").pack(side=LEFT, padx=2, pady=2)
        ttk.Button(layerFrame, text="-", width=3, command=self.ShowPrevLayer).pack(
            side=LEFT, padx=2, pady=2
        )
        self.label_beadsPhotoLayerID = ttk.Label(
            layerFrame, text=str(self.beadsPhotoLayerID)
        )
        self.label_beadsPhotoLayerID.pack(side=LEFT, padx=2, pady=2)
        ttk.Button(layerFrame, text="+", width=3, command=self.ShowNextLayer).pack(
            side=LEFT, padx=2, pady=2
        )
        layerFrame.grid(row=4, column=0, sticky="n")
        imageParamFrame.pack(side= TOP)

        parametersFrame.grid(row=1, column=1, sticky="NSWE")

        # ----------------------- Image Canvas Frame -----------------------------
        canvasFrame = Frame(self)

        self.mainPhotoCanvas = Canvas(
            canvasFrame, width=wwidth, height=wheight, bg="white"
        )
        self.mainPhotoCanvas.grid(row=0, column=0, sticky=(N, E, S, W))
        # main image scrollbars
        self.hScroll = ttk.Scrollbar(canvasFrame, orient="horizontal")
        self.vScroll = ttk.Scrollbar(canvasFrame, orient="vertical")
        self.hScroll.grid(row=1, column=0, columnspan=2, sticky=(E, W))
        self.vScroll.grid(row=0, column=1, sticky=(N, S))
        self.hScroll.config(command=self.mainPhotoCanvas.xview)
        self.mainPhotoCanvas.config(xscrollcommand=self.hScroll.set)
        self.vScroll.config(command=self.mainPhotoCanvas.yview)
        self.mainPhotoCanvas.config(yscrollcommand=self.vScroll.set)

        canvasFrame.grid(row=1, column=2, sticky="WENS")
        self.attributes("-topmost", True)

    # ---------------------- end __init__  ---------------------------------

    def AdjustBrightness(self,scalerValue):
        """
        Callback for Redraw canvas with current  brightness scaler value.
        """
        if self.imgBeadsRaw is None:
            return
        # brightness adjust
        self.brightnessValue = pow(2,float(scalerValue))
        self.AdjustImageBrightnessContrast()

    def AdjustContrast(self, scalerValue):
        """
        Callback for Redraw canvas with current  contrast scaler value.
        """
        if self.imgBeadsRaw is None:
            return
        # contrast adjust
        self.contrastValue = pow(2,float(scalerValue))
        self.AdjustImageBrightnessContrast()

    def AdjustImageBrightnessContrast(self):
        """
        Redraw canvas with current brightness and contrast scalers values.
        """
        enhancerBrightness = ImageEnhance.Brightness(self.imgBeadsRaw)
        imgCanvEnhaced = enhancerBrightness.enhance( self.brightnessValue )
        enhancerContrast = ImageEnhance.Contrast(imgCanvEnhaced)
        imgCanvEnhaced = enhancerContrast.enhance( self.contrastValue )
        self.imgCnv = ImageTk.PhotoImage(imgCanvEnhaced)
        self.mainPhotoCanvas.create_image(0, 0, image=self.imgCnv, anchor=NW)
        # updating scrollers
        self.mainPhotoCanvas.configure(scrollregion=self.mainPhotoCanvas.bbox("all"))
        self.DrawAllMarks()


    def ShowNextLayer(self):
        """Change visible layer"""
        self.beadsPhotoLayerID += 1
        if self.beadsPhotoLayerID > len(self.imgBeadsRawList) - 1:
            self.beadsPhotoLayerID = len(self.imgBeadsRawList) - 1
        # updating label on interface
        self.label_beadsPhotoLayerID.config(text=str(self.beadsPhotoLayerID))
        self.imgBeadsRaw = self.imgBeadsRawList[self.beadsPhotoLayerID]
        self.AdjustImageBrightnessContrast()

    def ShowPrevLayer(self):
        """Change visible layer"""
        self.beadsPhotoLayerID += -1
        if self.beadsPhotoLayerID < 0:
            self.beadsPhotoLayerID = 0
        # updating label on interface
        self.label_beadsPhotoLayerID.config(text=str(self.beadsPhotoLayerID))
        self.imgBeadsRaw = self.imgBeadsRawList[self.beadsPhotoLayerID]
        self.AdjustImageBrightnessContrast()

    def SetMainPhotoImageArray(self, ArrayIn = None):
        """Loading raw beads photo from file"""
        if ArrayIn is None:
            raise ValueError("No array provided", "no_file_path")
        try:
            self.imgBeadsRawList=[]
            for i in range(ArrayIn.shape[0]):
                tmpArray = ArrayIn[i,:,:].reshape((ArrayIn.shape[1],ArrayIn.shape[2]))
                # use .convert('L') when make array from numpyArray to avoid problem with F mode   
                # !caution! fromarray(tmpArray, mode="L") does not work as intended, so use convert('L').
                tmp = ImageOps.colorize(Image.fromarray(tmpArray).convert('L'),
                                        black="black",
                                        white="white",
                                        mid = self.mainImageColor)
                self.imgBeadsRawList.append(tmp)
                # ImageOps.colorize(self.imgBeadsRawList[i], black="green", white="white")
        except:
            raise ValueError(
                "Cant set canvas image with beads photo."
            )
        self.beadsPhotoLayerID = int((len(self.imgBeadsRawList) + 1) / 2)
        self.imgBeadsRaw = self.imgBeadsRawList[self.beadsPhotoLayerID]
        self.BeadMarksClear()
        # updating label on interface
        self.label_beadsPhotoLayerID.config(text=str(self.beadsPhotoLayerID))
        # preparing image for canvas from desired frame
        self.imgCnv = ImageTk.PhotoImage(
            image=self.imgBeadsRaw, master=self.mainPhotoCanvas
        )
        # replacing image on the canvas
        self.mainPhotoCanvas.create_image(
            (0, 0), image=self.imgCnv, state="normal", anchor=NW
        )
        # updating scrollers
        self.mainPhotoCanvas.configure(scrollregion=self.mainPhotoCanvas.bbox("all"))

    def SetFileInfo(self, infoStr: str):
        self.imageInfoStr.set(infoStr)

    
    def PlotCanvasInWindow(self, arrayIn: np.ndarray):
        top = Toplevel(self)
        top.geometry("600x600")
        cnvCompare = Canvas(top, width=590, height=590, bg="white")
        cnvCompare.pack(side=TOP, fill=BOTH, expand=True)
        figImg = AuxCanvasPlot.FigureCanvasTkFrom3DArray(
            arrayIn, cnvCompare, plotName=""
        )
        figImg.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        tk.Button(top, text="Close", command=lambda: top.destroy()).pack(side=TOP)

    def PlotBeadPreview2D(self, beadArray, winTitle="2D Plot"):
        """ "Plots three bead in XYZ planes"""
        child_tmp = tk.Toplevel(self)
        child_tmp.title(winTitle)
        cnvPlot = tk.Canvas(child_tmp, width=400, height=600)
        cnvPlot.pack(side="top", fill=BOTH)
        try:
            cnvTmp = AuxCanvasPlot.FigureCanvasTkFrom3DArray(
                beadArray, cnvPlot, " ", 300, 700
            )
            cnvTmp.get_tk_widget().pack(side="top", fill=BOTH)
        except Exception as e:
            raise RuntimeError("Bead 2D plot failed" + str(e))
        Button(child_tmp, text="Close", command=child_tmp.destroy).pack(side="top")

    def PlotBeadPreview3D(self, beadArray, winTitle="3D Plot"):
        """ "Plots three bead in 3D pointplot"""
        try:
            # popup window creation with canvas and exit button
            child_tmp = tk.Toplevel(self)
            child_tmp.title(winTitle)
            cnvPlot = tk.Canvas(child_tmp, width=300, height=300)
            cnvPlot.pack(side="top")
            Button(child_tmp, text="Close", command=child_tmp.destroy).pack(side="top")

            AuxCanvasPlot.FigureCanvasTk3DFrom3DArray(
                beadArray, cnvPlot
            ).get_tk_widget().pack(side="top")
        except Exception as e:
            raise RuntimeError("Bead 3D plot failed" + str(e))


if __name__ == "__main__":

    # need to SetProcessDPIAware to get correct resolution numbers for both TK and user32 method.
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    root = Tk()
    # print("Tk screen dimensions:", root.winfo_screenwidth(), root.winfo_screenheight())
    # print("user32 screen dimensions:", user32.GetSystemMetrics(78), user32.GetSystemMetrics(79))
    winWidth = user32.GetSystemMetrics(78)/4
    winHeight = user32.GetSystemMetrics(79)/3
    base1 = EditorView(root, winWidth, winHeight)
    base1.mainloop()
