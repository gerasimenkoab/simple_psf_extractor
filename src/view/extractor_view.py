import numpy as np
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from PIL import ImageTk, Image, ImageEnhance
try: 
    from .AuxTkPlot_class import AuxCanvasPlot
except:
    from AuxTkPlot_class import AuxCanvasPlot

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
        self.intensityFactor = 1.0  # intensity factor for beads selection widget
        self.beadsPhotoLayerID = 0  # default index of beads microscope photo

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

        #----------------------------- Menu Bar ----------------------------
        self.menubar = Menu(self)
        filemenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Load Image", underline = 0, accelerator= "Ctrl+o",
                             command = lambda: self.event_generate("<<LoadImageDialog>>"))
        filemenu.add_command(label="Save Selected Beads", underline = 0, command = lambda: self.event_generate("<<SaveSelectedBeads>>"))
        filemenu.add_command(label="Save Average Bead", underline = 1, command = lambda: self.event_generate("<<SaveAverageBead>>"))
        filemenu.add_separator()
        filemenu.add_command(label="Average Several Beads", underline = 1, command = lambda: self.event_generate("<<AverageSeveralBeads>>"))
        filemenu.add_separator()
        filemenu.add_command(label="Close", comman = lambda: self.event_generate("<<CloseExtractor>>"))

        editMenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=editMenu)
        editMenu.add_command(label="Set Voxel...", underline = 4, command = lambda: self.event_generate("<<SetVoxel>>"))
        editMenu.add_command(label="Set Bead Size...", underline = 4, command = lambda: self.event_generate("<<SetBeadSize>>"))

        selectionMenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Selection", menu=selectionMenu)
        selectionMenu.add_command(label="Set Selection Size...", command = lambda: self.event_generate("<<SetSelectionSize>>"))
        selectionMenu.add_command(label="Undo", underline = 0, accelerator = "Ctrl+z", command = lambda: self.event_generate("<<UndoSelect>>"))
        selectionMenu.add_command(label="Clear All", underline = 0, command = lambda: self.event_generate("<<ClearAllBeads>>"))


        helpMenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=helpMenu)
        helpMenu.add_command(label="Help", command = lambda: self.event_generate("<<ShowHelp>>"))
        helpMenu.add_command(label="About", command = lambda: self.event_generate("<<ShowAbout>>"))
        self.config(menu=self.menubar)

        #--------------------------- Menu Bar ------------------------------

        

        parametersFrame = ttk.Frame(self)

        # -------------- image and canvas frame --------------------------
        imageParamFrame= Frame(parametersFrame)
        ttk.Label(
            imageParamFrame,
            text="Image",
            font="Helvetica 10 bold",
        ).grid(row=0, column=0, sticky="n")

        self.imageInfoStr = tk.StringVar(value='No Image Loaded')
        self.imageInfo_lbl = ttk.Label(imageParamFrame, textvariable=self.imageInfoStr )
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
        ttk.Label(tiffTypeSelectFrame, width=10, text="Tiff type ").pack( side=LEFT, padx=2, pady=2 )
        self.tiffType_menu = ttk.OptionMenu(tiffTypeSelectFrame, self.tiffSaveBitType, *self.tiffMenuBitText)
        self.tiffType_menu.pack(side=LEFT, padx=2, pady=2)
        tiffTypeSelectFrame.grid(row=2, column=0, sticky="n")

        brightnessFrame = Frame(imageParamFrame)
        ttk.Button(brightnessFrame, text="-",width=3, command=self.LowerBrightnessToBeadSelectionWidget).pack(
            side=LEFT, padx=2, pady=2
        )
        ttk.Label(brightnessFrame, text="Brightness").pack(side=LEFT, padx=2, pady=2)
        ttk.Button(brightnessFrame, text="+", width=3,command=self.AddBrightnessToBeadSelectionWidget).pack(
            side=LEFT, padx=2, pady=2
        )
        brightnessFrame.grid(row=3, column=0, sticky="n")

        layerFrame = Frame(imageParamFrame)
        ttk.Label(layerFrame, text=" Layer:").pack(side=LEFT, padx=2, pady=2)
        ttk.Button(layerFrame, text="-",width=3, command=self.ShowPrevLayer).pack( side=LEFT, padx=2, pady=2 )
        self.label_beadsPhotoLayerID = ttk.Label(layerFrame, text=str(self.beadsPhotoLayerID))
        self.label_beadsPhotoLayerID.pack(side=LEFT, padx=2, pady=2)
        ttk.Button(layerFrame, text="+",width=3, command=self.ShowNextLayer).pack( side=LEFT, padx=2, pady=2 )
        layerFrame.grid(row=4, column=0, sticky="n")

        voxSizeFrame = Frame(imageParamFrame)
        ttk.Label(voxSizeFrame, text="Voxel size (\u03BCm): ", anchor="w").pack( side=TOP, padx=2, pady=2 )
        voxSizeFrame_low = Frame(voxSizeFrame)
        for key in ("Z", "Y", "X"):
            ttk.Label(voxSizeFrame_low, text=key + "= ").pack(side=LEFT, padx=2, pady=2)
            self.voxelSizeEntries[key] = ttk.Entry(
                voxSizeFrame_low, width=5            )
            self.voxelSizeEntries[key].pack(side=LEFT, padx=2, pady=2)
        voxSizeFrame_low.pack( side=TOP, padx=2, pady=2 )
        voxSizeFrame.grid(row=5, column=0, sticky="n")

        frameBeadSize = Frame(imageParamFrame)
        ttk.Label(frameBeadSize, width=20, text="Actual bead Size:", anchor="w").pack( side=LEFT, padx=2, pady=2 )
        self.beadSizeEntry = ttk.Entry(frameBeadSize, width=5)
        self.beadSizeEntry.pack(side=LEFT, padx=2, pady=2)
        ttk.Label(frameBeadSize, text="\u03BCm ").pack( side=LEFT )  # mu simbol encoding - \u03BC
        frameBeadSize.grid(row=6, column=0, sticky="n")


        imageParamFrame.pack(side=TOP)

        ttk.Separator(parametersFrame, orient="horizontal").pack(ipadx=100, pady=10)

        # ---------------------- Mark Beads Frame --------------------

        f2 = Frame(parametersFrame)
        ttk.Label(
            f2,
            text="Selection",
            font="Helvetica 10 bold",
        ).grid(row=0, column=0,sticky="n")

        selectSizeFrame = Frame(f2)
        ttk.Label(selectSizeFrame, width=14, text="Selection Size: ", anchor="w").pack(
            side=LEFT, padx=2, pady=2
        )
        self.selectSizeEntry = ttk.Entry(selectSizeFrame, width=5)
        self.selectSizeEntry.pack(side=LEFT, padx=2, pady=2)
        ttk.Label(selectSizeFrame, text="px").pack(side=LEFT, padx=2, pady=2)
        selectSizeFrame.grid(row=1, column=0, sticky="n")

        frameMarks = Frame(f2)
        self.autocorrectSelection = IntVar(value=1)
        ttk.Checkbutton(
            frameMarks,
            variable = self.autocorrectSelection,
            text="Auto-correction",
            onvalue=1,
            offvalue=0,
            width=15,
        ).pack(side=LEFT, padx=5, pady=2, fill=BOTH, expand=1)
        frameMarks.grid(row=2, column=0, sticky="n")

        f2.pack(side=TOP)
        ttk.Separator(parametersFrame, orient="horizontal").pack(ipadx=100, pady=10)


        # --------------- Average Beads Frame --------------------------
        frameAvrageBeads = Frame(parametersFrame)
        ttk.Label(
            frameAvrageBeads,
            text="Averaging",
            font="Helvetica 10 bold",
        ).pack(side=TOP)

        self.blurMenuTypeText = ["gauss", "none", "median"]
        self.blurApplyType = StringVar()
        self.blurApplyType.set(self.blurMenuTypeText[0])

        frameBlurTypeSelect = Frame(frameAvrageBeads)
        ttk.Label(frameBlurTypeSelect, width=10, text=" Blur type:").pack(
            side=LEFT, padx=2, pady=2
        )
        blurTypeSelect = ttk.Combobox(
            frameBlurTypeSelect,
            textvariable=self.blurApplyType,
            values=self.blurMenuTypeText,
            state="readonly",
        )
        blurTypeSelect.current(0)
        blurTypeSelect.pack(side=LEFT)
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
        ttk.Label(beadPrevHeaderFrame, text="Extracted Beads:").pack(side=LEFT, padx=2, pady=2)
        self.beadPrevHeaderVar = StringVar()
        ttk.Label(beadPrevHeaderFrame, textvariable=self.beadPrevHeaderVar).pack(side=LEFT, padx=2, pady=2)
        self.beadPrevHeaderVar.set( str(self._beadMarksCounter) )
        beadPrevHeaderFrame.pack(side=TOP, padx=2, pady=2)
        
        beadListboxFrame = tk.Frame(beadPreviewFrame)
        self.beadListBox = tk.Listbox(beadListboxFrame)
        self.beadListBox.pack(side=LEFT, fill = Y)
        s = ttk.Scrollbar(beadListboxFrame, orient=VERTICAL, command =self.beadListBox.yview)
        s.pack(side = LEFT,fill = Y)
        beadListboxFrame.pack(side=TOP, padx=5, pady=2, fill=BOTH, expand=True)

        beadPreviewMenuFrame = ttk.Frame(beadPreviewFrame)

        self.viewBead2d_btn = ttk.Button(beadPreviewMenuFrame, text="Bead 2D")
        self.viewBead2d_btn.pack(side=LEFT)
        self.viewBead3d_btn = ttk.Button(beadPreviewMenuFrame, text="Bead 3D")
        self.viewBead3d_btn.pack(side=LEFT)
        beadPreviewMenuFrame.pack(side=TOP, padx=2, pady=2)

        beadPreviewFrame.grid(row=1, column=4, sticky="NSWE")


        # ---------------------- end __init__  ---------------------------------



    def UpdateBeadSelectionWidgetImage(self):
        """
        Preparing image for canvas from desired frame with setted parameters.
        """
        # brightness adjust
        enhancer = ImageEnhance.Brightness(self.imgBeadsRaw)
        imgCanvEnhaced = enhancer.enhance(self.intensityFactor)

        self.imgCnv = ImageTk.PhotoImage(imgCanvEnhaced)
        self.mainPhotoCanvas.create_image(0, 0, image=self.imgCnv, anchor=NW)
        # updating scrollers
        self.mainPhotoCanvas.configure(scrollregion=self.mainPhotoCanvas.bbox("all"))
        self.DrawAllMarks()

    def AddBrightnessToBeadSelectionWidget(self):
        """Funcion increase intensity"""
        self.intensityFactor *= 1.1
        self.UpdateBeadSelectionWidgetImage()

    def LowerBrightnessToBeadSelectionWidget(self):
        """Funcion decrease intensity"""
        self.intensityFactor *= 0.9
        self.UpdateBeadSelectionWidgetImage()

    def ShowNextLayer(self):
        """Change visible layer"""
        self.beadsPhotoLayerID += 1
        if self.beadsPhotoLayerID > self.imgBeadsRaw.n_frames - 1:
            self.beadsPhotoLayerID = self.imgBeadsRaw.n_frames - 1
        # updating label on interface
        self.label_beadsPhotoLayerID.config(text=str(self.beadsPhotoLayerID))
        self.imgBeadsRaw.seek(self.beadsPhotoLayerID)
        self.UpdateBeadSelectionWidgetImage()

    def ShowPrevLayer(self):
        """Change visible layer"""
        self.beadsPhotoLayerID += -1
        if self.beadsPhotoLayerID < 0:
            self.beadsPhotoLayerID = 0
        # updating label on interface
        self.label_beadsPhotoLayerID.config(text=str(self.beadsPhotoLayerID))
        self.imgBeadsRaw.seek(self.beadsPhotoLayerID)
        self.UpdateBeadSelectionWidgetImage()

    def CloseMainPhotoFile(self):
        fileName = self.imgBeadsRaw.filename
        self.imgBeadsRaw.close()
        return fileName
    
    def SetMainPhotoImage(self, tmpFilePath=None):
        """Loading raw beads photo from file"""
        if tmpFilePath is None:
            raise FileNotFoundError("No file name provided", "no_file_path")
        try:
            try:
                self.imgBeadsRaw.close()
            except:
                pass
            self.imgBeadsRaw = Image.open(tmpFilePath)
        except:
            raise FileNotFoundError(
                "Cant set canvas image with beads photo.", "cant_read_file"
            )
        self.beadsPhotoLayerID = int((self.imgBeadsRaw.n_frames + 1) / 2)
        self.imgBeadsRaw.seek(self.beadsPhotoLayerID)
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

    def SetVoxelValues(self, voxelInDict):
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
        #change list VIEW
        self.SetMarkedBeadList()

    def SetMarkedBeadList(self):
        self.beadListBox.delete(0,tk.END)
        self.beadListBox.insert(0,*self.beadCoords)
        self.beadPrevHeaderVar.set( str(self._beadMarksCounter) )

    def beadListViewGet(self):
        print('curselection:', self.beadListBox.curselection()[0])
        return self.beadListBox.curselection()[0]

    def PlotCanvasInWindow(self, arrayIn: np.ndarray):
        top = Toplevel(self)
        top.geometry("600x600")
        cnvCompare = Canvas(top, width=590, height=590, bg="white")
        cnvCompare.pack(side=TOP, fill=BOTH, expand=True)
        figImg = AuxCanvasPlot.FigureCanvasTkFrom3DArray(
                arrayIn, cnvCompare, plotName=""            )
        figImg.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        tk.Button(top,text="Close",command = lambda :top.destroy()).pack(side=TOP)

    def PlotBeadPreview2D(self, beadArray, winTitle = '2D Plot'):
        """ "Plots three bead in XYZ planes"""
        child_tmp = tk.Toplevel( self )
        child_tmp.title( winTitle )
        cnvPlot = tk.Canvas( child_tmp, width=400, height=600 )
        cnvPlot.pack( side="top", fill=BOTH )
        try:
            cnvTmp = AuxCanvasPlot.FigureCanvasTkFrom3DArray(beadArray, cnvPlot, " ",300,700)
            cnvTmp.get_tk_widget().pack( side="top", fill=BOTH )
        except Exception as e:
            raise RuntimeError("Bead 2D plot failed" + str(e))
        Button(child_tmp, text="Close", command=child_tmp.destroy).pack(side="top")

    def PlotBeadPreview3D(self, beadArray, winTitle = '3D Plot'):
        """ "Plots three bead in 3D pointplot"""
        try:
            # popup window creation with canvas and exit button
            child_tmp = tk.Toplevel(self)
            child_tmp.title(winTitle)
            cnvPlot = tk.Canvas(child_tmp, width=300, height=300)
            cnvPlot.pack(side="top")
            Button(child_tmp, text="Close", command=child_tmp.destroy).pack(side="top")

            AuxCanvasPlot.FigureCanvasTk3DFrom3DArray(beadArray, cnvPlot).get_tk_widget().pack( side="top" )
        except Exception as e:
            raise RuntimeError("Bead 3D plot failed" + str(e))


if __name__ == "__main__":
    base1 = ExtractorView(Tk())
    base1.mainloop()
