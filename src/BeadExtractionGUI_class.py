import numpy as np
from scipy.special import jv  # Bessel function
from scipy.ndimage import gaussian_filter, median_filter
from scipy.interpolate import interpn
from scipy.interpolate import RegularGridInterpolator
import itertools
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo, askokcancel
from tkinter.filedialog import (
    askopenfilenames,
    askdirectory,
    asksaveasfilename,
)
from tkinter.simpledialog import askstring
from PIL import ImageTk, Image, ImageEnhance
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.cm as cm
import os
import json

# from os import path
from logging import raiseExceptions

import file_inout as fio
from plot_for_gui import FigureCanvasTkFrom3DArray, FigureCanvasTk3DFrom3DArray

# from  ImageRaw_class import ImageRaw

"""   TODO:
       - add  bead size to tiff tag
"""


class BeadExtractionGUI(tk.Toplevel):
    """Class provides instruments for extraction of beads from microscope multilayer photo."""

    def __init__(self, parent, wwidth=600, wheight=600):
        super().__init__(parent)
        # new  class properties
        self.beadCoords = []  # Coordinates of beads on the canvas
        self.beadMarks = []  # rectangle pics on the canvas
        self.intensityFactor = 1.0  # intensity factor for beads selection widget
        self.beadsPhotoLayerID = 0  # default index of beads microscope photo


        self.selectionFrameHalf = 18  # default selection halfsize

        self.beadDiameter = (
            0.2  # initial bead diameter in micrometers = diameter(nm)/1000
        )
        self.beadVoxelSize = [
            0.2,
            0.089,
            0.089,
        ]  # microscope voxel size(z,x,y) in micrometres (resolution=micrometre/pixel)
        self.voxelFields = "Z", "X", "Y"
        self.voxelSizeEntries = {}

        self.xr = 0
        self.yr = 0

        # new window widgets
        self.title("Bead extraction.")
        self.resizable(False, False)
        Label(
            self,
            text="Extract Beads Set from the Microscope Image",
            font="Helvetica 14 bold",
        ).grid(row=0, column=0, columnspan=2)

        f0 = Frame(self)
        # making frames to pack several fileds in one grid cell

        # -------------- image and canvas frame --------------------------
        f1 = Frame(f0)
        Label(
            f1,
            text="1. Load beads photos from the microscope and enter bead size and voxel parameters",
            font="Helvetica 10 bold",
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        f1_1 = Frame(f1)
        Button(f1_1, text="Load Beads Photo", command=self.LoadBeadsPhoto).pack(
            side=LEFT, padx=52, pady=2
        )
        Label(f1_1, text=" Adjust canvas brightness:").pack(side=LEFT, padx=2, pady=2)
        Button(f1_1, text="+", command=self.AddBrightnessToBeadSelectionWidget).pack(
            side=LEFT, padx=2, pady=2
        )
        Button(f1_1, text="-", command=self.LowerBrightnessToBeadSelectionWidget).pack(
            side=LEFT, padx=2, pady=2
        )
        Label(f1_1, text=" Layer:").pack(side=LEFT, padx=2, pady=2)
        Button(f1_1, text="+", command=self.ShowNextLayer).pack(
            side=LEFT, padx=2, pady=2
        )
        self.label_beadsPhotoLayerID = Label(f1_1, text=str(self.beadsPhotoLayerID))
        self.label_beadsPhotoLayerID.pack(side=LEFT, padx=2, pady=2)
        Button(f1_1, text="-", command=self.ShowPrevLayer).pack(
            side=LEFT, padx=2, pady=2
        )
        f1_1.grid(row=1, column=0, columnspan=2)
        frameBeadSize = Frame(f1)
        Label(frameBeadSize, width=20, text="Actual bead Size:", anchor="w").pack(
            side=LEFT, padx=2, pady=2
        )
        self.beadSizeEntry = Entry(frameBeadSize, width=5, bg="green", fg="white")
        self.beadSizeEntry.pack(side=LEFT, padx=2, pady=2)
        Label(frameBeadSize, text="\u03BCm ").pack(
            side=LEFT
        )  # mu simbol encoding - \u03BC
        frameBeadSize.grid(row=2, column=1, padx=2, pady=2, sticky="we")
        self.beadSizeEntry.insert(0, self.beadDiameter)
        self.beadSizeEntry.bind("<Return>", self.SetBeadSize)
        self.beadSizeEntry.bind("<FocusOut>", self.SetBeadSize)

        voxSizeFrame = Frame(f1)
        Label(voxSizeFrame, text="Voxel size (\u03BCm): ", anchor="w").pack(
            side=LEFT, padx=2, pady=2
        )
        for idField, voxelField in enumerate(self.voxelFields):
            Label(voxSizeFrame, text=voxelField + "=").pack(side=LEFT, padx=2, pady=2)
            ent = Entry(voxSizeFrame, width=5, bg="green", fg="white")
            ent.pack(side=LEFT, padx=2, pady=2)
            Label(voxSizeFrame, text=" ").pack(side=LEFT, padx=2, pady=2)
            ent.insert(0, self.beadVoxelSize[idField])
            ent.bind("<Return>", self.SetVoxelSize)
            ent.bind("<FocusOut>", self.SetVoxelSize)
            self.voxelSizeEntries[voxelField] = ent
        voxSizeFrame.grid(row=2, column=0, sticky="we")
        f1.pack(side=TOP)
        ttk.Separator(f0, orient="horizontal").pack(ipadx=200, pady=10)
        # ---------------------- Mark Beads Frame --------------------

        f2 = Frame(f0)
        Label(
            f2,
            text="2.Mark beads by right click on the window",
            font="Helvetica 10 bold",
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        selectSizeFrame = Frame(f2)
        Label(selectSizeFrame, width=20, text="Selection Size: ", anchor="w").pack(
            side=LEFT, padx=2, pady=2
        )
        self.selectSizeEntry = Entry(selectSizeFrame, width=5, bg="green", fg="white")
        self.selectSizeEntry.pack(side=LEFT, padx=2, pady=2)
        Label(selectSizeFrame, text="px").pack(side=LEFT, padx=2, pady=2)
        self.selectSizeEntry.insert(0, self.selectionFrameHalf * 2)
        self.selectSizeEntry.bind("<Return>", self.SetSelectionFrameSize)
        self.selectSizeEntry.bind("<FocusOut>", self.SetSelectionFrameSize)
        selectSizeFrame.grid(row=1, column=0, sticky="we")

        frameMarks = Frame(f2)
        Button(frameMarks, text="Undo mark", command=self.RemoveLastMark).pack(
            side=LEFT, padx=2, pady=2, fill=BOTH, expand=1
        )
        Button(frameMarks, text="Clear All Marks", command=self.ClearAllMarks).pack(
            side=LEFT, padx=2, pady=2, fill=BOTH, expand=1
        )
        frameMarks.grid(row=1, column=1, sticky="we")
        f2.pack(side=TOP)
        ttk.Separator(f0, orient="horizontal").pack(ipadx=200, pady=10)

        # ------------------- Extract Beads Frame ------------------------
        f3 = Frame(f0)
        Label(
            f3, text="3. Extract selected beads and save set", font="Helvetica 10 bold"
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        Button(f3, text="Extract Selected Beads", command=self.ExtractBeads).grid(
            row=1, column=0, padx=2, pady=2, sticky="we"
        )

        Button(f3, text="Save Extracted Beads", command=self.SaveSelectedBeads).grid(
            row=1, column=1, padx=2, pady=2, sticky="we"
        )

        self.tiffMenuBitText = ["8 bit", "16 bit", "32 bit"]
        self.tiffMenuBitDict = {
            "8 bit": "uint8",
            "16 bit": "uint16",
            "32 bit": "uint32",
        }
        self.tiffSaveBitType = StringVar()
        self.tiffSaveBitType.set(self.tiffMenuBitText[0])

        frameTiffTypeSelect = Frame(f3)
        Label(frameTiffTypeSelect, width=10, text="Tiff type ").pack(
            side=LEFT, padx=2, pady=2
        )
        OptionMenu(
            frameTiffTypeSelect, self.tiffSaveBitType, *self.tiffMenuBitText
        ).pack(side=LEFT, padx=2, pady=2)
        frameTiffTypeSelect.grid(row=1, column=2, padx=2, pady=2, sticky="we")

        f3.pack(side=TOP)
        ttk.Separator(f0, orient="horizontal").pack(ipadx=200, pady=10)

        # --------------- Average Beads Frame --------------------------
        frameAvrageBeads = Frame(f0)
        Label(
            frameAvrageBeads,
            text="4. Calculate averaged bead with desired blur type and save it.",
            font="Helvetica 10 bold",
        ).pack(side=TOP)

        self.blurMenuTypeText = ["gauss", "none", "median"]
        self.blurApplyType = StringVar()
        self.blurApplyType.set(self.blurMenuTypeText[0])

        frameBlurTypeSelect = Frame(frameAvrageBeads)
        Label(frameBlurTypeSelect, width=10, text=" Blur type:").pack(
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
        self.doRescaleOverZ = IntVar(value=0)
        Checkbutton(
            frameBlurTypeSelect,
            variable=self.doRescaleOverZ,
            text=" equal XYZ scale",
            onvalue=1,
            offvalue=0,
        ).pack(side=LEFT, padx=2, pady=2)
        self.precessBeadPrev = IntVar(value=0)
        Checkbutton(
            frameBlurTypeSelect,
            variable=self.precessBeadPrev,
            text=" preview bead",
            onvalue=1,
            offvalue=0,
        ).pack(side=LEFT, padx=2, pady=2)

        frameBlurTypeSelect.pack(side=TOP, padx=2, pady=2)

        frameAvrageBeadsButtons = Frame(frameAvrageBeads)
        Button(
            frameAvrageBeadsButtons,
            text="Average Bead",
            command=self.BeadsArithmeticMean,
        ).pack(side=LEFT, padx=2, pady=2, fill=BOTH, expand=1)
        Button(
            frameAvrageBeadsButtons,
            text="Save Average Bead",
            command=self.SaveAverageBead,
        ).pack(side=LEFT, padx=2, pady=2, fill=BOTH, expand=1)
        frameAvrageBeadsButtons.pack(side=TOP)
        frameAvrageBeads.pack(side=TOP)  # grid(row =6,column = 0,sticky='we')

        # frameIdealBead = Frame(self)
        # Button(frameIdealBead,text = 'Save Plane Bead', command = self.SavePlaneSphereBead).pack(side = LEFT,padx=2,pady=2,fill=BOTH,expand=1)
        # Button(frameIdealBead, text = 'Save Airy Bead', command = self.SaveAirySphereBead).pack(side = LEFT, padx=2,pady=2,fill=BOTH,expand = 1)
        # frameIdealBead.grid(row =7,column = 0,sticky='we')

        ttk.Separator(f0, orient="horizontal").pack(ipadx=200, pady=10)
        Button(f0, text="Average Several Beads", command=self.AvrageManyBeads).pack(
            side=TOP, padx=2, pady=2
        )  # grid(row = 6, column = 3,padx=2,pady=2, sticky = 'we')

        f0.grid(row=1, column=0, sticky="NSWE")

        Button(f0, text="Close", command=self.CloseWindow).pack(
            side=TOP, padx=2, pady=2
        )  # grid(row = 6, column = 3,padx=2,pady=2, sticky = 'we')

        f0.grid(row=1, column=0, sticky="NSWE")

        # ---------------- Bead Photo Frame -----------------------------
        canvasFrame = Frame(self)
        self.cnv1 = Canvas(canvasFrame, width=wwidth, height=wheight, bg="white")
        self.cnv1.grid(row=0, column=0, sticky=(N, E, S, W))
        # main image scrollbars
        self.hScroll = Scrollbar(canvasFrame, orient="horizontal")
        self.vScroll = Scrollbar(canvasFrame, orient="vertical")
        self.hScroll.grid(row=1, column=0, columnspan=2, sticky=(E, W))
        self.vScroll.grid(row=0, column=1, sticky=(N, S))
        self.hScroll.config(command=self.cnv1.xview)
        self.cnv1.config(xscrollcommand=self.hScroll.set)
        self.vScroll.config(command=self.cnv1.yview)
        self.cnv1.config(yscrollcommand=self.vScroll.set)
        # mark bead with right click
        self.cnv1.bind("<Button-3>", self.BeadMarkClick)
        canvasFrame.grid(row=1, column=1, sticky="WENS")

        # -------------- Bead Preview Frame -----------------------------
        beadPreviewFrame = Frame(self)

        # test bead display canvas. May be removed. if implemented separate window.
        Label(beadPreviewFrame, text="Bead Preview").pack(side=TOP, padx=2, pady=2)
        self.cnvImg = Canvas(beadPreviewFrame, width=190, height=570, bg="white")
        self.cnvImg.pack(side=TOP, padx=2, pady=2)

        beadPreviewMenuFrame = Frame(beadPreviewFrame)
        self.beadPrevNum = Entry(beadPreviewMenuFrame, width=5)
        self.beadPrevNum.pack(side=LEFT)
        self.beadPrevNum.insert(0, len(self.beadCoords))
        Button(
            beadPreviewMenuFrame, text="Bead 2D", command=self.PlotBeadPreview2D
        ).pack(side=LEFT)
        Button(
            beadPreviewMenuFrame, text="Bead 3D", command=self.PlotBeadPreview3D
        ).pack(side=LEFT)
        beadPreviewMenuFrame.pack(side=TOP, padx=2, pady=2)
        beadPreviewFrame.grid(row=1, column=2, sticky="NSWE")

    def Foo(self):
        """placeholder function"""
        pass
        print("do nothing.")

    def CloseWindow(self):
        """Closing window and clear tmp files"""
        # Checking existance of self.imgBeadsRaw.close()
        if askokcancel("Close", "Close Bead Extractor Widget?"):
            try:
                self.imgBeadsRaw.close()
            except:
                print("Can't close imgBeadsRaw image")
            tmppath = os.getcwd() + "\\tmp.tiff"
            if os.path.exists(tmppath):
                try:
                    os.remove(tmppath)
                except:
                    print("Can't remove " + tmppath)
            else:
                print("File not exist: " + tmppath)
            self.destroy()

    def UpdateBeadSelectionWidgetImage(self):
        """Preparing image for canvas from desired frame with setted parameters."""
        # brightness adjust
        enhancer = ImageEnhance.Brightness(self.imgBeadsRaw)
        imgCanvEnhaced = enhancer.enhance(self.intensityFactor)

        self.imgCnv = ImageTk.PhotoImage(imgCanvEnhaced)
        self.cnv1.create_image(0, 0, image=self.imgCnv, anchor=NW)
        # updating scrollers
        self.cnv1.configure(scrollregion=self.cnv1.bbox("all"))
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

    # def Bead2Arrays(self, beadID):
    #     bead = self.selectedBeads[int(beadID)]
    #     # теперь разбрасываем бид по отдельным массивам .
    #     print("shape:", bead.shape[0], bead.shape[1], bead.shape[2])
    #     zcoord = np.zeros(bead.shape[0] * bead.shape[1] * bead.shape[2])
    #     xcoord = np.zeros(bead.shape[0] * bead.shape[1] * bead.shape[2])
    #     ycoord = np.zeros(bead.shape[0] * bead.shape[1] * bead.shape[2])
    #     voxelVal = np.zeros(bead.shape[0] * bead.shape[1] * bead.shape[2])
    #     nn = 0
    #     bead = bead / np.amax(bead) * 255.0
    #     for i, j, k in itertools.product(
    #         range(bead.shape[0]), range(bead.shape[1]), range(bead.shape[2])
    #     ):
    #         if bead[i, j, k] > np.exp(-1):
    #             zcoord[nn] = i
    #             xcoord[nn] = j
    #             ycoord[nn] = k
    #             voxelVal[nn] = bead[i, j, k]
    #             #                 voxelVal[voxelVal < 0.5] = 0
    #             nn = nn + 1
    #     plotFlag = 0
    #     if plotFlag == 1:
    #         fig = plt.figure()
    #         ax = fig.add_subplot(111, projection="3d")
    #         n = nn - 1
    #         im = ax.scatter(
    #             xcoord[0:n],
    #             ycoord[0:n],
    #             zcoord[0:n],
    #             c=voxelVal[0:n],
    #             alpha=0.5,
    #             cmap=cm.jet,
    #         )
    #         fig.colorbar(im)
    #         ax.set_xlabel("X Label")
    #         ax.set_ylabel("Y Label")
    #         ax.set_zlabel("Z Label")
    #         plt.show()
    #     return zcoord, xcoord, ycoord, voxelVal

    def PlotBead3D(self, bead, treshold=np.exp(-1) * 255.0):
        """Plot 3D view of a given bead"""
        # popup window creation with canvas and exit button
        child_tmp = tk.Toplevel(self)
        child_tmp.title("3D Bead Preview") 
        cnvPlot = tk.Canvas(child_tmp,width=300,height=300)
        cnvPlot.pack(side='top')
        Button(child_tmp, text="Close", command=child_tmp.destroy).pack(side='top')
      
        FigureCanvasTk3DFrom3DArray( bead, cnvPlot ).get_tk_widget().pack(side='top')
    

    # def UpscaleBead3D(self, bead, plotPreview=False):
    #     """Upscale of a given bead"""
    #     # теперь разбрасываем бид по отдельным массивам .
    #     zcoord = np.zeros(bead.shape[0])
    #     xcoord = np.zeros(bead.shape[1])
    #     ycoord = np.zeros(bead.shape[2])
    #     zcoordR = np.zeros(bead.shape[1])
    #     bead = bead / np.amax(bead) * 255.0
    #     # new code
    #     #            maximum = np.amax(bead)
    #     #            maxcoords = np.unravel_index(np.argmax(bead, axis=None), bead.shape)
    #     #            print("maxcoords:",maxcoords)
    #     #
    #     print(
    #         "range test:",
    #         np.linspace(0.0, bead.shape[0], num=bead.shape[0], endpoint=False),
    #     )
    #     zcoord = np.arange(bead.shape[0]) * self.beadVoxelSize[0]
    #     xcoord = np.arange(bead.shape[1]) * self.beadVoxelSize[1]
    #     ycoord = np.arange(bead.shape[2]) * self.beadVoxelSize[2]
    #     # shift to compensate rescale move relative to center
    #     shift = (
    #         bead.shape[0] * self.beadVoxelSize[0]
    #         - bead.shape[1] * self.beadVoxelSize[1]
    #     ) * 0.5
    #     #            shift = maxcoords[0] * self.beadVoxelSize[0] - bead.shape[1] * self.beadVoxelSize[1] * 0.5
    #     zcoordR = shift + np.arange(bead.shape[1]) * self.beadVoxelSize[1]
    #     interp_fun = RegularGridInterpolator((zcoord, xcoord, ycoord), bead)

    #     pts = np.array(list(itertools.product(zcoordR, xcoord, ycoord)))
    #     pts_ID = list(
    #         itertools.product(
    #             np.arange(bead.shape[1]),
    #             np.arange(bead.shape[1]),
    #             np.arange(bead.shape[1]),
    #         )
    #     )
    #     ptsInterp = interp_fun(pts)
    #     beadInterp = np.ndarray((bead.shape[1], bead.shape[1], bead.shape[1]))
    #     for pID, p_ijk in enumerate(pts_ID):
    #         beadInterp[p_ijk[0], p_ijk[1], p_ijk[2]] = ptsInterp[pID]
    #     if plotPreview == True:
    #         figUpsc, figUpscAxs = plt.subplots(3, 1, sharex=False, figsize=(2, 6))
    #         figUpsc.suptitle("Image preview")
    #         figUpscAxs[0].pcolormesh(
    #             beadInterp[beadInterp.shape[0] // 2, :, :], cmap=cm.jet
    #         )
    #         figUpscAxs[1].pcolormesh(
    #             beadInterp[:, beadInterp.shape[1] // 2, :], cmap=cm.jet
    #         )
    #         figUpscAxs[2].pcolormesh(
    #             beadInterp[:, :, beadInterp.shape[2] // 2], cmap=cm.jet
    #         )

    #         newWin = Toplevel(self)
    #         newWin.geometry("200x600")
    #         newWin.title("Image ")
    #         cnvFigUpsc = Canvas(newWin, width=200, height=600, bg="white")
    #         cnvFigUpsc.pack(side=TOP, fill=BOTH, expand=True)
    #         FigureCanvasTkAgg(figUpsc, cnvFigUpsc).get_tk_widget().pack(
    #             side=TOP, fill=BOTH, expand=True
    #         )

    #     # fig, axs = plt.subplots(3, 1, sharex = False, figsize=(2,6))
    #     # axs[0].pcolormesh(beadInterp[beadInterp.shape[0] // 2,:,:],cmap=cm.jet)
    #     # axs[1].pcolormesh(beadInterp[:,beadInterp.shape[1] // 2,:],cmap=cm.jet)
    #     # axs[2].pcolormesh(beadInterp[:,:,beadInterp.shape[2] // 2],cmap=cm.jet)
    #     # plt.show()
    #     return beadInterp

    # def UpscaleBead_Zaxis(self, bead, plotPreview=False):
    #     """Upscale along Z axis of a given bead"""
    #     # теперь разбрасываем бид по отдельным массивам .
    #     zcoord = np.zeros(bead.shape[0])
    #     xcoord = np.zeros(bead.shape[1])
    #     ycoord = np.zeros(bead.shape[2])
    #     zcoordR = np.zeros(
    #         bead.shape[1]
    #     )  # shape of rescaled bead in Z dimension  - same as x shape
    #     #            bead = bead/np.amax(bead)*255.0 # normalize bead intensity
    #     maxcoords = np.unravel_index(np.argmax(bead, axis=None), bead.shape)
    #     #            print("maxcoords:",maxcoords)

    #     zcoord = np.arange(bead.shape[0]) * self.beadVoxelSize[0]
    #     xcoord = np.arange(bead.shape[1]) * self.beadVoxelSize[1]
    #     ycoord = np.arange(bead.shape[2]) * self.beadVoxelSize[2]
    #     # shift to compensate rescale move relative to center
    #     #            shift = (bead.shape[0] * self.beadVoxelSize[0] - bead.shape[1] * self.beadVoxelSize[1]) * 0.5
    #     # fixed shift now depends on center of the bead
    #     shift = (
    #         maxcoords[0] * self.beadVoxelSize[0]
    #         - bead.shape[1] * self.beadVoxelSize[1] * 0.5
    #     )
    #     zcoordR = shift + np.arange(bead.shape[1]) * self.beadVoxelSize[1]
    #     interp_fun = RegularGridInterpolator((zcoord, xcoord, ycoord), bead)

    #     pts = np.array(list(itertools.product(zcoordR, xcoord, ycoord)))
    #     pts_ID = list(
    #         itertools.product(
    #             np.arange(bead.shape[1]),
    #             np.arange(bead.shape[1]),
    #             np.arange(bead.shape[1]),
    #         )
    #     )
    #     ptsInterp = interp_fun(pts)
    #     beadInterp = np.ndarray((bead.shape[1], bead.shape[1], bead.shape[1]))
    #     for pID, p_ijk in enumerate(pts_ID):
    #         beadInterp[p_ijk[0], p_ijk[1], p_ijk[2]] = ptsInterp[pID]
    #     self.__upscaledBead = np.ndarray((bead.shape[1], bead.shape[1], bead.shape[1]))
    #     self.__upscaledBead = beadInterp
    #     self.beadVoxelSize[0] = self.beadVoxelSize[1]
    #     if plotPreview == True:  # draw 3 projections of bead
    #         figUpsc, figUpscAxs = plt.subplots(3, 1, sharex=False, figsize=(2, 6))
    #         figUpsc.suptitle("Image preview")
    #         figUpscAxs[0].pcolormesh(
    #             beadInterp[beadInterp.shape[0] // 2, :, :], cmap=cm.jet
    #         )
    #         figUpscAxs[1].pcolormesh(
    #             beadInterp[:, beadInterp.shape[1] // 2, :], cmap=cm.jet
    #         )
    #         figUpscAxs[2].pcolormesh(
    #             beadInterp[:, :, beadInterp.shape[2] // 2], cmap=cm.jet
    #         )

    #         newWin = Toplevel(self)
    #         newWin.geometry("200x600")
    #         newWin.title("Image ")
    #         cnvFigUpsc = Canvas(newWin, width=200, height=600, bg="white")
    #         cnvFigUpsc.pack(side=TOP, fill=BOTH, expand=True)
    #         FigureCanvasTkAgg(figUpsc, cnvFigUpsc).get_tk_widget().pack(
    #             side=TOP, fill=BOTH, expand=True
    #         )

    #     return beadInterp


    def LoadBeadsPhoto(self):
        """Loading raw beads photo from file"""
        fileList = askopenfilenames(title="Load Beads Photo")
        if len(fileList) > 1:
            self.imgCnvArr = fio.ReadTiffMultFiles(fileList)
            try:
                self.beadsPhotoLayerID = int(len(fileList) / 2)
                tmppath = os.getcwd() + "\\tmp.tiff"
                # Checking existance of self.imgBeadsRaw.close()
                try:
                    self.imgBeadsRaw.close()
                except:
                    pass
                fio.SaveAsTiffStack(self.imgCnvArr, tmppath)
                self.imgBeadsRaw = Image.open(tmppath)
                self.imgBeadsRaw.seek(self.beadsPhotoLayerID)
                self.ClearAllMarks()
            except:
                showerror("Error", " Multifile load: Can't read file for canvas")
                return
        elif len(fileList) == 1:
            beadImPath = fileList[0]
            print("read one file", beadImPath)
            self.imgCnvArr = fio.ReadTiffStackFile(beadImPath)
            try:
                self.imgBeadsRaw = Image.open(beadImPath)
                print(self.imgBeadsRaw.mode)
                print("Number of frames: ", self.imgBeadsRaw.n_frames)
                self.beadsPhotoLayerID = int(self.imgBeadsRaw.n_frames / 2)
                print("Frame number for output: ", self.beadsPhotoLayerID)
                # setting imgTmp to desired number
                self.imgBeadsRaw.seek(self.beadsPhotoLayerID)
                self.ClearAllMarks()
            except:
                showerror("Error", "Singlefile load: Can't read file for canvas.")
                return
        else:
            showerror("Error", "Load Beads Photo: No files selected to load.")
            return
        # updating label on interface
        self.label_beadsPhotoLayerID.config(text=str(self.beadsPhotoLayerID))
        # preparing image for canvas from desired frame
        self.imgCnv = ImageTk.PhotoImage(image = self.imgBeadsRaw, master = self.cnv1)
        # replacing image on the canvas
        self.cnv1.create_image((0, 0), image=self.imgCnv, state = 'normal', anchor=NW)
        # updating scrollers
        self.cnv1.configure(scrollregion=self.cnv1.bbox("all"))

    def AvrageManyBeads(self):
        """
        Loading many same size bead files and calculate the arithmetic mean.
        Output: file with averaged bead.
        """
        beadsArray = self.LoadManyBeads()
        if beadsArray != None:
            averagedArray = sum(beadsArray) / len(beadsArray)
            fio.SaveAsTiffStack(averagedArray,asksaveasfilename())


    def LoadManyBeads(self):
        """Loading many raw bead photos from files"""
        fileList = askopenfilenames(title="Load Bead Photos")
        beadsList = []
        dimensions = []
        if len(fileList) < 1:
            showerror("No bead files selected.")
            return None
        else:
            fPath = fileList[0]
            newArray = fio.ReadTiffStackFile(fPath)
            dimensions = newArray.shape
            beadsList.append( newArray )
            for fPath in fileList[1:]:
                try:
                    newArray = fio.ReadTiffStackFile(fPath)
                    print(dimensions,newArray.shape,fPath)
                    if dimensions == newArray.shape:
                        print(dimensions == newArray.shape)
                        beadsList.append( newArray )
                    else:
                        showerror( "Error", "Beads must have the same dimensions. Wrong size at: " + fPath )
                        return None
                except Exception as exc:
                    showerror("Error", "Beads load for averaging failed.")
                    print(exc)
                    return
        return beadsList
    
    


    def BeadMarkClick(self, event):
        """Append mouse event coordinates to global list. Center is adjusted according to max intensity."""
        cnv = event.widget
        self.xr, self.yr = cnv.canvasx(event.x), cnv.canvasy(event.y)
        self.xr, self.yr = self.LocateFrameMAxIntensity3D()
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
        self.beadCoords.append([self.xr, self.yr])

    def DrawAllMarks(self):
        """Draw marks for beads on main canvas(cnv1)"""
        cnv = self.cnv1
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


    def LocateFrameMAxIntensity3D(self):
        """Locate point with maximum intensity in current 3d array.
        In: array - np.array
        Out: coords - list
        """
        d = self.selectionFrameHalf
        # dimension 0 - its z- plane
        # dimension 1 - y
        # dimension 2 - x
        xi = self.xr
        yi = self.yr
        bound3 = int(xi - d)
        bound4 = int(xi + d)
        bound1 = int(yi - d)
        bound2 = int(yi + d)
        #                  print("coords: ",bound1,bound2,bound3,bound4)
        sample = self.imgCnvArr[:, bound1:bound2, bound3:bound4]
        maximum = np.amax(sample)
        coords = np.unravel_index(np.argmax(sample, axis=None), sample.shape)
        #            print("LocateMaxIntensity: coords:", coords)
        return coords[2] + bound3, coords[1] + bound1

    def RemoveLastMark(self):
        """Removes the last bead in the list"""
        self.beadCoords.pop()
        self.cnv1.delete(self.beadMarks[-1])
        self.beadMarks.pop()

    def ClearAllMarks(self):
        """Clears all bead marks"""
        self.beadCoords = []
        for sq in self.beadMarks:
            self.cnv1.delete(sq)
        self.beadMarks = []


    def SetVoxelSize(self, event):
        """Bead voxel size change"""
        zeroTreshold = 0.0000001
        for idField, vField in enumerate(self.voxelFields):
            tmp = self.voxelSizeEntries[vField].get()
            try:
                self.beadVoxelSize[idField] = abs( float(tmp) )
                if self.beadVoxelSize[idField] < zeroTreshold:
                    self.beadVoxelSize[idField] = zeroTreshold
            except:
                showerror("Set Voxel Size: ", "Bad input: not a Float.")
                self.voxelSizeEntries[vField].delete(0, END)
                self.voxelSizeEntries[vField].insert(0, self.beadVoxelSize[idField])
                return

    def SetBeadSize(self, event):
        """Bead diameter size change"""
        tmp = self.beadSizeEntry.get()
        try:
            self.beadDiameter = abs( float(tmp) )
            self.beadSizeEntry.delete( 0, END )
            self.beadSizeEntry.insert( 0, str(self.beadDiameter) )
        except:
            showerror("Bead Size: ", "Bad input")
            self.beadSizeEntry.delete( 0, END )
            self.beadSizeEntry.insert( 0, str(self.beadDiameter) )
            return

    def SetSelectionFrameSize(self, event):
        """Selection Frame size change"""
        tmp = self.selectSizeEntry.get()
        try:
            self.selectionFrameHalf = int(abs(float(tmp)) / 2)
            self.selectSizeEntry.delete(0, END)
            self.selectSizeEntry.insert(0, str(self.selectionFrameHalf * 2))
        except:
            showerror("Selection size: ", "Bad input")
            self.selectSizeEntry.delete(0, END)
            self.selectSizeEntry.insert(0, self.selectionFrameHalf * 2)
            return


    def ExtractBeads(self):
        """Extracting bead stacks from picture set and centering them"""
        self.selectedBeads = []
        d = self.selectionFrameHalf
        print(self.imgCnvArr.shape)
        elem = np.ndarray([self.imgCnvArr.shape[0], d * 2, d * 2])
        for idx, i in enumerate(self.beadCoords):
            bound3 = int(i[0] - d)
            bound4 = int(i[0] + d)
            bound1 = int(i[1] - d)
            bound2 = int(i[1] + d)
            #                  print("coords: ",bound1,bound2,bound3,bound4)
            elem = self.imgCnvArr[:, bound1:bound2, bound3:bound4]
            # shifting array max intesity toward center along Z axis
            iMax = np.unravel_index(np.argmax(elem, axis=None), elem.shape)
            zc = int(elem.shape[0] / 2)
            shift = zc - iMax[0]
            elem = np.roll(elem, shift=shift, axis=0)
            iMax = np.unravel_index(np.argmax(elem, axis=None), elem.shape)
            self.selectedBeads.append(elem)

    def SaveSelectedBeads(self):
        """Save selected beads as multi-page tiffs as is."""
        if hasattr(self, "selectedBeads"):
            txt_folder_enquiry = askdirectory()

            txt_prefix = ""
            if txt_prefix == "":
                txt_prefix = "bead_"
            dirId = -1
            while True:
                dirId += 1
                txt_folder = txt_folder_enquiry + "/" + "bead_folder_" + str(dirId)
                if not os.path.isdir(txt_folder):
                    print("creating dir", txt_folder)
                    os.mkdir(txt_folder)
                    break
            tiffBit = self.tiffMenuBitDict[self.tiffSaveBitType.get()]
            
            #strVoxel = "Voxel(\u03BCm) :" + ';'.join(str(s) for s in self.beadVoxelSize)
            strVoxel = json.dumps({"Z":self.beadVoxelSize[0],"X":self.beadVoxelSize[1],"Y":self.beadVoxelSize[2]})
            for idx, bead in enumerate(self.selectedBeads):
                fname = txt_folder + "/" + str(idx).zfill(2) + ".tif"
                fio.SaveAsTiffStack_tag(bead, fname, outtype = tiffBit, tagID = 270, tagString = strVoxel)
            showinfo("Selected beads tiffs saved at saved at:", txt_folder)

    def PlotBeadPreview2D(self):
        """ "Plots three bead in XYZ planes"""
        if len(self.beadCoords) <= 0:
            showerror("PlotBeadPreview", "Error. No beads selected")
        elif not hasattr(self, "selectedBeads"):
            showerror("PlotBeadPreview", "Error. Beads are not extracted.")
        else:
            tmp = self.beadPrevNum.get()
            #                  self.BeadAsArrays(0)
            if not tmp.isnumeric():
                showerror("PlotBeadPreview", "Bad input")
                self.beadPrevNum.delete(0, END)
                self.beadPrevNum.insert(0, str(len(self.selectedBeads) - 1))
                return
            else:
                try:
                    self.imgBeadRaw = self.selectedBeads[int(tmp)]
                    self.figIMG_canvas_agg = FigureCanvasTkFrom3DArray(self.imgBeadRaw, self.cnvImg, plotName = "Bead 2D")
                    self.figIMG_canvas_agg.get_tk_widget().grid(
                        row=1, column=5, rowspan=10, sticky=(N, E, S, W)
                    )
                except IndexError:
                    showerror("PlotBeadPreview", "Index out of range.")
                    self.beadPrevNum.delete(0, END)
                    self.beadPrevNum.insert(0, str(len(self.selectedBeads) - 1))

    def PlotBeadPreview3D(self):
        """ "Plots three bead in 3D pointplot"""
        if len(self.beadCoords) <= 0:
            showerror("PlotBeadPreview", "Error. No beads selected")
        elif not hasattr(self, "selectedBeads"):
            showerror("PlotBeadPreview", "Error. Beads are not extracted.")
        else:
            tmp = self.beadPrevNum.get()
            #                  self.BeadAsArrays(0)
            if not tmp.isnumeric():
                showerror("PlotBeadPreview", "Bad input")
                self.beadPrevNum.delete(0, END)
                self.beadPrevNum.insert(0, str(len(self.selectedBeads) - 1))
                return
            else:
                try:
                    self.PlotBead3D(self.selectedBeads[int(tmp)])
                except IndexError:
                    showerror("PlotBeadPreview", "Index out of range.")
                    self.beadPrevNum.delete(0, END)
                    self.beadPrevNum.insert(0, str(len(self.selectedBeads) - 1))

    def BlurBead(self, bead, blurType, plotPreview=False):
        """
        Blur bead with selected filter
        """
        #            blurType = self.blurApplyType.get()
        if blurType == "gauss":
            bead = gaussian_filter(bead, sigma=1)
        elif blurType == "median":
            bead = median_filter(bead, size=3)

        if plotPreview == True:  # draw 3 projections of bead
            figUpsc, figUpscAxs = plt.subplots(3, 1, sharex=False, figsize=(2, 6))
            figUpsc.suptitle("Image preview")
            figUpscAxs[0].pcolormesh(bead[bead.shape[0] // 2, :, :], cmap=cm.jet)
            figUpscAxs[1].pcolormesh(bead[:, bead.shape[1] // 2, :], cmap=cm.jet)
            figUpscAxs[2].pcolormesh(bead[:, :, bead.shape[2] // 2], cmap=cm.jet)

            newWin = Toplevel(self)
            newWin.geometry("200x600")
            newWin.title("Image ")
            cnvFigUpsc = Canvas(newWin, width=200, height=600, bg="white")
            cnvFigUpsc.pack(side=TOP, fill=BOTH, expand=True)
            FigureCanvasTkAgg(figUpsc, cnvFigUpsc).get_tk_widget().pack(
                side=TOP, fill=BOTH, expand=True
            )

        return bead

    def BeadsArithmeticMean(self):
        #            print("blurtype", self.blurApplyType.get(), "rescale Z", self.doRescaleOverZ.get() )
        if not hasattr(self, "selectedBeads"):
            showerror("Error", "Extract beads first.")
        else:
            self.__avrageBead = sum(self.selectedBeads) / len(self.selectedBeads)
            self.__avrageBead = self.BlurBead(
                self.__avrageBead, self.blurApplyType.get()
            )
            if self.doRescaleOverZ.get() == 1:
                self.__avrageBead = self.UpscaleBead_Zaxis(self.__avrageBead)
            if self.precessBeadPrev.get() == 1:  # draw 3 projections of bead
                figUpsc, figUpscAxs = plt.subplots(3, 1, sharex=False, figsize=(2, 6))
                figUpsc.suptitle("Image preview")
                figUpscAxs[0].pcolormesh(
                    self.__avrageBead[self.__avrageBead.shape[0] // 2, :, :],
                    cmap=cm.jet,
                )
                figUpscAxs[1].pcolormesh(
                    self.__avrageBead[:, self.__avrageBead.shape[1] // 2, :],
                    cmap=cm.jet,
                )
                figUpscAxs[2].pcolormesh(
                    self.__avrageBead[:, :, self.__avrageBead.shape[2] // 2],
                    cmap=cm.jet,
                )

                newWin = Toplevel(self)
                newWin.geometry("200x600")
                newWin.title("Image ")
                cnvFigUpsc = Canvas(newWin, width=200, height=600, bg="white")
                cnvFigUpsc.pack(side=TOP, fill=BOTH, expand=True)
                FigureCanvasTkAgg(figUpsc, cnvFigUpsc).get_tk_widget().pack(
                    side=TOP, fill=BOTH, expand=True
                )

    def SaveAverageBead(self):
        """Save averaged bead to file"""
        tiffBit = self.tiffMenuBitDict[self.tiffSaveBitType.get()]
        #strVoxel = "Voxel(\u03BCm) :" + ';'.join(str(s) for s in self.beadVoxelSize)
        strVoxel = json.dumps({"Z":self.beadVoxelSize[0],"X":self.beadVoxelSize[1],"Y":self.beadVoxelSize[2]})
        filesMask = [('All Files', '*.*'), 
             ('TIFF file', '*.tif')]
        try:
            fname = asksaveasfilename(
                filetypes = filesMask,
                defaultextension = filesMask,
                initialfile = "averagebead.tif")
        except Exception as e:
            print(e)
            return
        try:
            fio.SaveAsTiffStack_tag(self.__avrageBead, fname, outtype = tiffBit, tagID = 270, tagString = strVoxel)
        except Exception as e:
            print(e)
            return




if __name__ == "__main__":
    base1 = BeadExtractionGUI(Tk())
    base1.mainloop()
