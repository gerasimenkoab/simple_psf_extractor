import numpy as np
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from PIL import ImageTk, Image, ImageEnhance, ImageOps

try:
    from ..common.AuxTkPlot_class import AuxCanvasPlot
except:
    from common.AuxTkPlot_class import AuxCanvasPlot

"""   TODO:
        - fix  AuxTkPlot_class  for all modules
       - add  bead size to tiff tag
"""


class ExtractorView(tk.Toplevel):
    """Class provides instruments for extraction of beads from microscope multilayer photo."""

    def __init__(self, parent, wwidth=600, wheight=600):
        super().__init__(parent)
        # new  class properties
        self.beadMarks = []  # rectangle pics on the canvas
        self._beadMarksCounter = 0
        self.beadCoords = []
        self.beadsPhotoLayerID = 0  # default index of beads microscope photo
        self.imgBeadsRaw = None
        self.brightnessValue = 1
        self.contrastValue = 1
        self.mainImageColor = "green" #"red"

        

        self.voxelFields = "Z", "X", "Y"
        self.voxelSizeEntries = {}

        self.xr = 0
        self.yr = 0
        self.button_name = {
            "LoadBeadsPhoto": "Load Beads Photo",
            "UndoMark": "Undo Mark",
            "ClearAllMark": "Clear All Marks",
            "ExtractSelectedBeads": "Extract Selected Beads",
            "SaveExtractedBeads": "Save Extracted Beads",
            "AutoSegmentBeads": "Auto-segment Beads",
            "ProcessExtractedBeads": "Process Extracted Beads",
            "SaveAverageBead": "Save Bead",
            "AverageSeveralBeads": "Average Several Beads",
            "Bead2D": "Show bead in 2D",
            "Bead3D": "Show bead in 3D",
            "Close": "Close Extractor",
        }
        self.button_dict = {}  # according to list of names {id_name : widget}
        self.entry_dict = {}  # according to list of names {id_name : widget}
        self.label_dict = {}  # label {id_name : string}
        # new window widgets
        self.title("Bead extractor")
        self.resizable(False, False)

        # ----------------------------- Menu Bar ----------------------------
        self.menubar = Menu(self)
        filemenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(
            label="Load Image",
            underline=0,
            accelerator="Ctrl+o",
            command=lambda: self.event_generate("<<LoadImageDialog>>"),
        )
        filemenu.add_command(
            label="Save Selected Beads",
            underline=0,
            command=lambda: self.event_generate("<<SaveSelectedBeads>>"),
        )
        filemenu.add_command(
            label="Save Average Bead",
            underline=1,
            command=lambda: self.event_generate("<<SaveAverageBead>>"),
        )
        filemenu.add_separator()
        filemenu.add_command(
            label="Average Several Beads",
            underline=1,
            command=lambda: self.event_generate("<<AverageSeveralBeads>>"),
        )
        filemenu.add_separator()
        filemenu.add_command(
            label="Close", comman=lambda: self.event_generate("<<CloseExtractor>>")
        )


        selectionMenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Selection", menu=selectionMenu)
        selectionMenu.add_command(
            label="Undo",
            underline=0,
            accelerator="Ctrl+z",
            command=lambda: self.event_generate("<<UndoSelect>>"),
        )
        selectionMenu.add_command(
            label="Clear All",
            underline=0,
            command=lambda: self.event_generate("<<ClearAllBeads>>"),
        )
        selectionMenu.add_separator()
        selectionMenu.add_command(
            label="Bead Previewer",
            underline=0,
            command=lambda: self.event_generate("<<PreviewBeads>>"),
        )

        helpMenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=helpMenu)
        helpMenu.add_command(
            label="Help", command=lambda: self.event_generate("<<ShowHelp>>")
        )
        self.config(menu=self.menubar)

        # --------------------------- End Menu Bar ------------------------------

        parametersFrame = ttk.Frame(self)

        # -------------- image and canvas frame --------------------------
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

        voxSizeFrame = Frame(imageParamFrame)
        ttk.Label(voxSizeFrame, text="Voxel size (\u03BCm): ", anchor="w").pack(
            side=TOP, padx=2, pady=2
        )
        voxSizeFrame_low = Frame(voxSizeFrame)
        for key in ("Z", "Y", "X"):
            ttk.Label(voxSizeFrame_low, text=key + "= ").pack(side=LEFT, padx=2, pady=2)
            self.voxelSizeEntries[key] = ttk.Entry(voxSizeFrame_low, width=5)
            self.voxelSizeEntries[key].pack(side=LEFT, padx=2, pady=2)
        voxSizeFrame_low.pack(side=TOP, padx=2, pady=2)
        voxSizeFrame.grid(row=5, column=0, sticky="n")

        frameBeadSize = Frame(imageParamFrame)
        ttk.Label(frameBeadSize, width=20, text="Actual bead Size:", anchor="w").pack(
            side=LEFT, padx=2, pady=2
        )
        self.beadSizeEntry = ttk.Entry(frameBeadSize, width=5)
        self.beadSizeEntry.pack(side=LEFT, padx=2, pady=2)
        ttk.Label(frameBeadSize, text="\u03BCm ").pack(
            side=LEFT
        )  # mu simbol encoding - \u03BC
        frameBeadSize.grid(row=6, column=0, sticky="n")

        imageParamFrame.pack(side=TOP)

        ttk.Separator(parametersFrame, orient="horizontal").pack(ipadx=100, pady=10)

        # ---------------------- Mark Beads Frame --------------------

        f2 = ttk.Frame(parametersFrame)
        ttk.Label(
            f2,
            text="Selection",
            font="Helvetica 10 bold",
        ).grid(row=0, column=0, sticky="n")

        # Selection Size Frame
        selectionFrame = ttk.Frame(f2)
        ttk.Label(selectionFrame, width=14, text="Selection Size: ", anchor="w").pack(
            side=LEFT, padx=2, pady=2
        )
        self.selectSizeEntry = ttk.Entry(selectionFrame, width=5)
        self.selectSizeEntry.pack(side=LEFT, padx=2, pady=2)
        ttk.Label(selectionFrame, text="px").pack(side=LEFT, padx=2, pady=2)
        selectionFrame.grid(row=1, column=0, sticky="n")

        # Max Area Size Frame
        maxAreaFrame = ttk.Frame(f2)
        ttk.Label(maxAreaFrame, width=14, text="Max area size: ", anchor="w").pack(
            side=LEFT, padx=2, pady=2
        )
        self.maxAreaEntry = ttk.Entry(maxAreaFrame, width=5)
        self.maxAreaEntry.pack(side=LEFT, padx=2, pady=2)
        ttk.Label(maxAreaFrame, text="px").pack(side=LEFT, padx=2, pady=2)
        maxAreaFrame.grid(row=2, column=0, sticky="n")

        # Auto-correction Checkbox Frame
        frameMarks = ttk.Frame(f2)
        self.autocorrectSelection = IntVar(value=1)
        ttk.Checkbutton(
            frameMarks,
            variable=self.autocorrectSelection,
            text="Auto-correction",
            onvalue=1,
            offvalue=0,
            width=15,
        ).pack(side=LEFT, padx=5, pady=2, fill=BOTH, expand=1)
        frameMarks.grid(row=3, column=0, sticky="n")

        # Auto-segment Beads Button Frame
        frameAutosegmBeads = ttk.Frame(f2)
        self.autoSegmentBeads_btn = ttk.Button(
            frameAutosegmBeads,
            text="Auto-segment Beads",
        )
        self.autoSegmentBeads_btn.pack(side=LEFT, padx=2, pady=2, fill=BOTH, expand=1)
        frameAutosegmBeads.grid(row=4, column=0, sticky="n")

        f2.pack(side=TOP, padx=10, pady=10)
        ttk.Separator(parametersFrame, orient="horizontal").pack(ipadx=100, pady=10)

        # --------------- Average Beads Frame --------------------------
        frameAvrageBeads = Frame(parametersFrame)
        ttk.Label(
            frameAvrageBeads,
            text="Processing",
            font="Helvetica 10 bold",
        ).pack(side=TOP)

        self.blurMenuTypeText = [ "none","gauss", "median"]
        self.blurApplyType = StringVar()
        self.blurApplyType.set(self.blurMenuTypeText[0])

        frameBlurTypeSelect = Frame(frameAvrageBeads)
        ttk.Label(frameBlurTypeSelect, width=10, text=" Denoise:").pack(
            side=LEFT, padx=2, pady=2
        )
        self.blurTypeSelect = ttk.Combobox(
            frameBlurTypeSelect,
            textvariable=self.blurApplyType,
            values=self.blurMenuTypeText,
            state="readonly",
        )
        self.blurTypeSelect.current(0)
        self.blurTypeSelect.pack(side=LEFT)
        frameBlurTypeSelect.pack(side=TOP, padx=2, pady=2)
        self.precessBeadPrev = IntVar(value=0)
        ttk.Checkbutton(
            frameAvrageBeads,
            variable=self.precessBeadPrev,
            text=" Preview processed bead ",
            onvalue=1,
            offvalue=0,
        ).pack(side=TOP, padx=2, pady=2)

        frameAvrageBeadsButtons = Frame(frameAvrageBeads)
        self.processBeads_btn = ttk.Button(
            frameAvrageBeadsButtons,
            text="Process Extracted Beads",
        )
        self.processBeads_btn.pack(side=LEFT, padx=2, pady=2, fill=BOTH, expand=1)
        frameAvrageBeadsButtons.pack(side=TOP)
        frameAvrageBeads.pack(side=TOP)

        parametersFrame.grid(row=1, column=0, sticky="NSWE")
        # ---------------- End of parameters frame description -----------------
        # ttk.Separator(self, orient="vertical").grid(column = 1, ipadx=10, pady=100)

        # ----------------------- Bead Photo Frame -----------------------------
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

        # -------------- Bead Preview Frame -----------------------------
        beadPreviewFrame = Frame(self)

        beadPrevHeaderFrame = tk.Frame(beadPreviewFrame)
        ttk.Label(beadPrevHeaderFrame, text="Extracted Beads:").pack(
            side=LEFT, padx=2, pady=2
        )
        self.beadPrevHeaderVar = StringVar()
        ttk.Label(beadPrevHeaderFrame, textvariable=self.beadPrevHeaderVar).pack(
            side=LEFT, padx=2, pady=2
        )
        self.beadPrevHeaderVar.set(str(self._beadMarksCounter))
        beadPrevHeaderFrame.pack(side=TOP, padx=2, pady=2)

        beadListboxFrame = tk.Frame(beadPreviewFrame)
        self.beadListBox = tk.Listbox(beadListboxFrame)
        self.beadListBox.pack(side=LEFT, fill=Y)
        s = ttk.Scrollbar(
            beadListboxFrame, orient=VERTICAL, command=self.beadListBox.yview
        )
        s.pack(side=LEFT, fill=Y)
        beadListboxFrame.pack(side=TOP, padx=5, pady=2, fill=BOTH, expand=True)

        beadPreviewMenuFrame = ttk.Frame(beadPreviewFrame)

        beadPreviewMenuFrame.pack(side=TOP, padx=2, pady=2)

        beadPreviewFrame.grid(row=1, column=4, sticky="NSWE")
   
        self._bindEvents()

        # bring widget in the center of the screen
        # self.attributes("-topmost", True)
        # OR
        # self.update_idletasks()
        # self.lift()


        # ---------------------- end __init__  ---------------------------------

    def _bindEvents(self):
        """Default local events binder"""
        # menus:
        # File:
        # self.bind("<<LoadImageDialog>>",self.LoadsBeadPhoto)
        # self.bind("<Control-o>",self.LoadsBeadPhoto)
        # self.bind("<<SaveSelectedBeads>>",self.SaveExtractedBeads)
        # self.bind("<<SaveAverageBead>>",self.SaveAverageBead)
        # self.bind("<<AverageSeveralBeads>>",self.AverageSeveralBeads)
        self.bind("<<CloseExtractor>>",self.CloseExtractor)
        # Selection:

        # self.bind("<<UndoSelect>>",self.UndoMark)
        # self.bind("<Control-z>",self.UndoMark)
        # self.bind("<<ClearAllBeads>>",self.ClearMarks)
        # self.bind("<<PreviewBeads>>",self.PreviewBeads)

        # Help:
        # self.bind("<<ShowHelp>>",self.ShowExtractorHelp)

        # buttons:
        # self.processBeads_btn.config(command=self.ProcessBeads)


    def SetDenoiseOptionsList(self, denoiseList: list)->None:
        """Set list of denoise methods"""
        if denoiseList is None:
            raise ValueError("No denoise list provided", "denoise_list_is_none")
        self.blurMenuTypeText = denoiseList
        # update menu option for self.blurTypeSelect with denoiseList
        self.blurTypeSelect["values"] = self.blurMenuTypeText
        self.blurApplyType.set(self.blurMenuTypeText[0])


    def AdjustBrightness(self,scalerValue)->None:
        """
        Callback for Redraw canvas with current  brightness scaler value.
        """
        if self.imgBeadsRaw is None:
            return
        # brightness adjust
        self.brightnessValue = pow(2,float(scalerValue))
        self.AdjustImageBrightnessContrast()

    def AdjustContrast(self, scalerValue)->None:
        """
        Callback for Redraw canvas with current  contrast scaler value.
        """
        if self.imgBeadsRaw is None:
            return
        # contrast adjust
        self.contrastValue = pow(2,float(scalerValue))
        self.AdjustImageBrightnessContrast()

    def AdjustImageBrightnessContrast(self)->None:
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


    def ShowNextLayer(self)->None:
        """Change visible layer"""
        self.beadsPhotoLayerID += 1
        if self.beadsPhotoLayerID > len(self.imgBeadsRawList) - 1:
            self.beadsPhotoLayerID = len(self.imgBeadsRawList) - 1
        # updating label on interface
        self.label_beadsPhotoLayerID.config(text=str(self.beadsPhotoLayerID))
        self.imgBeadsRaw = self.imgBeadsRawList[self.beadsPhotoLayerID]
        self.AdjustImageBrightnessContrast()

    def ShowPrevLayer(self)->None:
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

    def SetVoxelValues(self, voxelInDict: dict):
        """Bead voxel size change"""
        if voxelInDict is None:
            raise ValueError("No voxel values recived", "voxel_is_none")
        for axisName in voxelInDict:
            self.voxelSizeEntries[axisName].delete(0, END)
            self.voxelSizeEntries[axisName].insert(0, voxelInDict[axisName])

    def SetBeadSize(self, valueIn):
        """Bead diameter size change"""
        try:
            beadDiameter = abs(float(valueIn))
            self.beadSizeEntry.delete(0, END)
            self.beadSizeEntry.insert(0, str(beadDiameter))
        except:
            showerror("Bead Size: ", "Bad input")
            self.beadSizeEntry.delete(0, END)
            self.beadSizeEntry.insert(0, str(beadDiameter))
            return

    def SetSelectionFrameSize(self, valueIn):
        """Selection Frame size change"""
        try:
            self.selectionFrameHalf = int(abs(float(valueIn)) / 2)
            self.selectSizeEntry.delete(0, END)
            self.selectSizeEntry.insert(0, str(self.selectionFrameHalf * 2))
        except:
            showerror("Selection size: ", "Bad input")
            self.selectSizeEntry.delete(0, END)
            self.selectSizeEntry.insert(0, self.selectionFrameHalf * 2)
            return

    def SetMaxArea(self, valueIn):
        """Max area Bead change"""
        try:
            self.maxArea = int(abs(valueIn))
            self.maxAreaEntry.delete(0, END)
            self.maxAreaEntry.insert(0, str(self.maxArea))
        except:
            showerror("Max area size: ", "Bad input")
            self.maxAreaEntry.delete(0, END)
            self.maxAreaEntry.insert(0, self.maxArea)
            return

    def DrawAllMarks(self):
        """Draw marks for beads on main canvas(cnv1)"""
        cnv = self.mainPhotoCanvas
        for self.xr, self.yr in self.beadCoords:
            self.beadMarks.append(
                cnv.create_rectangle(
                    self.xr - self.selectionFrameHalf,
                    self.yr - self.selectionFrameHalf,
                    self.xr + self.selectionFrameHalf,
                    self.yr + self.selectionFrameHalf,
                    outline="chartreuse1",
                    width=2,
                )
            )

    def beadMarkAdd(self, widget, xr, yr):
        """
        Adding bead mark to canvas after mouse RBclick
        In:
            widget : canvas vidget name
            xr, yr : click event coordinates on widget
        """
        halfSide = int(self.selectSizeEntry.get()) // 2
        self.beadMarks.append(
            widget.create_rectangle(
                xr - halfSide,
                yr - halfSide,
                xr + halfSide,
                yr + halfSide,
                outline="chartreuse1",
                width=2,
            )
        )
        self.beadCoords.append([xr, yr])
        self._beadMarksCounter += 1
        self.SetMarkedBeadList()

    def BeadMarksRemoveId(self,Id):
        """Removes the last bead in the list"""
        if self.beadMarks == []:
            return
        try:
            self.mainPhotoCanvas.delete(self.beadMarks[Id])
            self.beadMarks.pop(Id)
            self.beadCoords.pop(Id)
        except:
            ValueError("Cant delete mark.")
        self._beadMarksCounter -= 1
        self.SetMarkedBeadList()


    def BeadMarksRemoveLast(self):
        """Removes the last bead in the list"""
        if self.beadMarks == []:
            return
        try:
            self.mainPhotoCanvas.delete(self.beadMarks[-1])
            self.beadMarks.pop()
            self.beadCoords.pop()
        except:
            ValueError("Cant delete mark.")
        self._beadMarksCounter -= 1
        self.SetMarkedBeadList()

    def BeadMarksClear(self):
        """Clears all bead marks"""
        if self.beadMarks == []:
            return
        for sq in self.beadMarks:
            self.mainPhotoCanvas.delete(sq)
        self.beadMarks = []
        self.beadCoords = []
        self._beadMarksCounter = 0
        # change list VIEW
        self.SetMarkedBeadList()

    def SetMarkedBeadList(self):
        self.beadListBox.delete(0, tk.END)
        self.beadListBox.insert(0, *self.beadCoords)
        self.beadPrevHeaderVar.set(str(self._beadMarksCounter))

    def beadListViewGet(self):
        return self.beadListBox.curselection()[0]

    def PlotCanvasInWindow(self, arrayIn: np.ndarray):
        top = Toplevel(self)
        top.geometry("300x900")
        top.title("Bead Preview")
        cnvCompare = Canvas(top, width=290, height=870, bg="white")
        cnvCompare.pack(side=TOP, fill=BOTH, expand=True)

        figImg = AuxCanvasPlot.FigurePILImagekFrom3DArray(arr3D = arrayIn)
         # Calculate the aspect ratio of the original image
        original_aspect_ratio = figImg.width / figImg.height

        # Calculate the new width and height while keeping the aspect ratio
        canvas_width = cnvCompare.winfo_reqwidth()
        canvas_height = cnvCompare.winfo_reqheight()
        canvas_aspect_ratio = canvas_width / canvas_height

        if canvas_aspect_ratio > original_aspect_ratio:
            # Canvas is wider than image, so set height to canvas height and scale width
            new_height = canvas_height
            new_width = int(new_height * original_aspect_ratio)
        else:
            # Canvas is taller than image, so set width to canvas width and scale height
            new_width = canvas_width
            new_height = int(new_width / original_aspect_ratio)

        # Resize the image
        figImg = figImg.resize((new_width, new_height))

        # Convert the PIL image to a PhotoImage
        self.tk_image = ImageTk.PhotoImage(figImg)

        # Draw the image on the canvas
        cnvCompare.create_image(0, 0, image=self.tk_image, anchor='nw')
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
        
    def CloseExtractor(self, event=None):
        """Default close window method """
        self.destroy()

    def AutoSegmentation(self, beadCoords):
        self.BeadMarksClear()
        self.beadCoords = beadCoords
        self._beadMarksCounter = len(self.beadCoords)
        self.DrawAllMarks()
        self.SetMarkedBeadList()


if __name__ == "__main__":
    base1 = ExtractorView(tk.Tk())
    base1.focus_force()
    base1.mainloop()
