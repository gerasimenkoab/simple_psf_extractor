import numpy as np
from tkinter import *
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image

from editor.editor_view_menu import EditorMenuBar


#    TODO:
#         - 



class EditorView(tk.Toplevel):
    """Class provides instruments for extraction of beads from microscope multilayer photo."""

    def __init__(self, parent, wwidth=600, wheight=600):
        super().__init__(parent)
        self.beadsPhotoLayerID = 0  # default index of beads microscope photo
        self.brightnessValue = 1
        self.contrastValue = 1
        self.mainImageColor = "green" # default color of the main image

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
        try:        
            self.menubar = EditorMenuBar(self)
            self.config(menu=self.menubar)
        except Exception as e:
            raise ValueError("Can't create menu bar", "menu-creation-failed")
        # --------------------------- End Menu Bar ------------------------------


        # -------------- image and canvas frame --------------------------

        parametersFrame = Frame(self)
        imageParamFrame = Frame(parametersFrame)
        imageParamFrame.grid_columnconfigure(0, minsize=200)  # Set minimum width for the first column
        # imageParamFrame.grid_propagate(False)  # Prevent the frame from shrinking
        ttk.Label(
            imageParamFrame,
            text="Image",
            font="Helvetica 10 bold",
        ).grid(row=0, column=0, sticky="n")

        self.imageInfoStr = tk.StringVar(value="No Image Loaded")
        self.imageInfo_lbl = ttk.Label(imageParamFrame, textvariable=self.imageInfoStr)
        self.imageInfo_lbl.grid(row=1, column=0, sticky="n")

        tiffTypeSelectFrame = Frame(imageParamFrame)
        # self.tiffMenuBitDict = {
        #     "8 bit": "uint8",
        #     "16 bit": "uint16",
        #     "32 bit": "uint32",
        # }
        self.tiffMenuBitDict = {
            "8 bit": "L",
            "16 bit": "I;16",
            "32 bit": "I;32",
            "RGB": "RGB",
        }
        self.tiffSaveBitType = StringVar()
        self.tiffSaveBitType.set( list(self.tiffMenuBitDict.keys())[0] )
        ttk.Label(tiffTypeSelectFrame, text="Tiff type ", width=12).pack(
            side=LEFT, padx=2, pady=2
        )
        self.tiffType_menu = ttk.OptionMenu(
            tiffTypeSelectFrame, 
            self.tiffSaveBitType, 
            self.tiffSaveBitType.get(),  # Add the current value to the values list (avoid value vanish error when changing the value)
            *list(self.tiffMenuBitDict.keys())
        )
        self.tiffType_menu.configure(width=10)
        self.tiffSaveBitType.set(list(self.tiffMenuBitDict.keys())[0])
        self.tiffType_menu.pack(side=LEFT, padx=2, pady=2)
        tiffTypeSelectFrame.grid(row=2, column=0, sticky="n")

#  option menu for color selection and variable for color
        self.colorList = ["green", "red", "blue"]
        self.mainImageColor = StringVar()
        colorSelectFrame = Frame(imageParamFrame)
        ttk.Label(colorSelectFrame, text = "Image Color:", width = 12).pack(side=LEFT, padx=2, pady=2)
        self.colorMenu = ttk.OptionMenu(
            colorSelectFrame, 
            self.mainImageColor, 
            self.mainImageColor.get(),  # Add the current value to the values list (avoid error when changing the value)
            *self.colorList
        )
        self.colorMenu.configure(width=10)
        self.mainImageColor.set(self.colorList[0])
        self.mainImageColor.trace_add("write", self.onImageColorChanged)
        self.colorMenu.pack(side=LEFT, padx=2, pady=2)
        colorSelectFrame.grid(row=3, column=0, sticky="n")



        brightnessFrame = Frame(imageParamFrame)
        ttk.Label(brightnessFrame, text="Brightness").pack(side=tk.TOP, padx=2, pady=2)
        self.brightnessScaleVar = DoubleVar()
        self.brightnessScale = ttk.Scale(brightnessFrame, orient='horizontal', from_=-8, to_=8,
                                         variable = self.brightnessScaleVar)
        self.brightnessScale.configure( command= self.onBrightnessScaleChanged )
        self.brightnessScale.pack(side=tk.TOP)
        ttk.Label(brightnessFrame, text="Contrast").pack(side=tk.TOP, padx=2, pady=2)
        self.contrastScale = ttk.Scale(brightnessFrame, orient='horizontal', from_=-8, to_=8)
        self.contrastScale.configure( command= self.onContrastScaleChanged )
        self.contrastScale.pack(side=tk.TOP)
        self.setScalersToDefault()

        brightnessFrame.grid(row=4, column=0, sticky="n")


        layerFrame = Frame(imageParamFrame)

        ttk.Label(layerFrame, text=" Layer:").pack(side=LEFT, padx=2, pady=2)
        self.buttonLayerSub = ttk.Button(layerFrame, text="-", width=3, command=self.onClickLayerNumberDecrease).pack(
            side=LEFT, padx=2, pady=2
        )
        self.label_beadsPhotoLayerID = ttk.Label(
            layerFrame, text=str(self.beadsPhotoLayerID)
        )
        self.label_beadsPhotoLayerID.pack(side=LEFT, padx=2, pady=2)
        self.buttonLayerAdd = ttk.Button(layerFrame, text="+", width=3, command=self.onClickLayerNumberIncrease).pack(
            side=LEFT, padx=2, pady=2
        )
        layerFrame.grid(row=5, column=0, sticky="n")
        imageParamFrame.pack(side= TOP)

        parametersFrame.grid(row=1, column=1, sticky="NSWE")

        # ----------------------- Image Canvas Frame -----------------------------
        canvasFrame = Frame(self)

        self.mainPhotoCanvas = Canvas(
            canvasFrame, width=wwidth, height=wheight, bg="white"
        )
        self.mainPhotoCanvas.grid(row=0, column=0, sticky=(N, E, S, W))
        self.update()

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

    def setScalersToDefault(self):
        self.brightnessScale.set(1)
        self.contrastScale.set(1)

    def onBrightnessScaleChanged(self, value):
        # generate event for brightness change
        self.event_generate("<<BrightnessScaleChanged>>")

    def onContrastScaleChanged(self, value):
        # generate event for contrast change
        self.event_generate("<<ContrastScaleChanged>>")

    def onImageColorChanged(self, *args):
        self.event_generate("<<ImageColorChanged>>")

    def onClickLayerNumberIncrease(self):
        self.event_generate("<<LayerUp>>")

    def onClickLayerNumberDecrease(self):
        self.event_generate("<<LayerDown>>")

    def setLayerNumber(self, layerNumber:int):
        """Set current shown layer number on the label"""
        self.label_beadsPhotoLayerID.config(text=str(layerNumber))

    def GetScalersValues(self):
        """Return current values of brightness and contrast scalers"""
        
        return pow(2,float(self.brightnessScale.get())), pow(2,float(self.contrastScale.get()))

    def DrawImageOnCanvas(self, img:Image = None):
        """Draw image on canvas"""
        if img is None:
            return
        # Get the width and height of the canvas
        canvas_width = self.mainPhotoCanvas.winfo_width()
        canvas_height = self.mainPhotoCanvas.winfo_height()
        # Resize the image to the size of the canvas
        imgResized = img.resize((canvas_width, canvas_height))
        self.imgCnv = ImageTk.PhotoImage(image=imgResized, master=self.mainPhotoCanvas)
        self.mainPhotoCanvas.create_image((0, 0), image=self.imgCnv, state="normal", anchor=NW)
        # updating scrollers
        self.mainPhotoCanvas.configure(scrollregion=self.mainPhotoCanvas.bbox("all"))

    # update this method later
    def SetFileInfo(self, infoStr: str):
        self.imageInfoStr.set(infoStr)

    def GetTiffBitType(self):
        return self.tiffMenuBitDict[self.tiffSaveBitType.get()]
    # function to get color from option menu
    def GetImageColor(self):
        return self.mainImageColor.get()