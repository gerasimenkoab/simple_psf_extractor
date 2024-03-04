import file_inout as fio
import deconvolution as decon
import img_transform as imtrans
from ImageRaw_class import ImageRaw

from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo, askokcancel
from tkinter.simpledialog import askstring
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.filedialog import askopenfilenames
from tkinter.ttk import Combobox, Separator
from PIL import ImageTk, Image
from PIL.TiffTags import TAGS

import os.path
from os import path
import json
import time
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as plticker
import matplotlib.cm as cm
from scipy.ndimage import gaussian_filter

from old_files.plot_for_gui import FigureCanvasTkFrom3DArray

import numpy as np
import itertools
from scipy.interpolate import interpn
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import zoom

import traceback

"""
TODO: 
    

"""

class DeconvolutionGUI(tk.Toplevel):
    def __init__(self, parent, wwidth=800, wheight=2000):
        super().__init__(parent)
        #self.gui_var_dict ={}
        self.deconMethodsDict = {
            "Richardson-Lucy":"RL",
            "Richardson-Lucy TM Reg":"RLTMR",
            "Richardson-Lucy TV Reg":"RLTVR"
            }
     
        self.beadVoxelSize = [
            0.2,
            0.089,
            0.089,
        ]  # microscope voxel size(z,x,y) in micrometres (resolution=micrometre/pixel)
        self.voxelFields = "Z", "X", "Y"
        self.voxelSizeEntries = {}

        #interface description

        self.title("Simple experimental PSF extractor")
        self.resizable(False, False)
        Label(self, text = "PSF  calculation:", font = "Helvetica 14 bold").grid(row = 0, column = 1)  # blanc insert
        f1 = Frame(self)
        Label(f1, text = "").grid(row = 0, column = 0)  # blanc insert
        Label(
            f1,
            text = "1. Load avaraged bead image created with bead extractor application.",
            font = "Helvetica 10 bold",
        ).grid(row = 1, column = 0, columnspan = 3, sticky = "w")
        f1ButtonEntryFrame = Frame(f1)
        Button(f1ButtonEntryFrame, width = 10 , text = "Load image", command = self.LoadBeadImageFile).pack(side = LEFT, padx=10)
        self.beadImgPathW = Entry(f1ButtonEntryFrame, width = 60, bg = "white", fg = "black")
        self.beadImgPathW.insert(0, "No Image Loaded" )
        self.beadImgPathW.configure(state = "readonly")
        self.beadImgPathW.pack( side = LEFT )
        f1ButtonEntryFrame.grid(row = 2, column = 0, columnspan = 2, sticky = "w")
        Separator( f1, orient="horizontal" ).grid( row = 3, column = 0, ipadx = 200, pady = 10, columnspan = 3 )
        f1.grid(column = 1, row = 1, sticky = "WE")

        f2 = Frame(self)
        Label(f2, text = "2. Fill Bead Image Parameters", font = "Helvetica 10 bold").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )  # blanc insert
        Label(f2, text="Bead size(nm):").grid(row=1, column=0)
        self.beadSizeWgt = Entry(f2, width=15, bg="white", fg="black")
        self.beadSizeWgt.grid(row=1, column=1, sticky="w")

        Label(f2, text="Resolution XY Z (nm/pixel):").grid(row=2, column=0)
        self.beadImXYResWgt = Entry(f2, width=15, bg="white", fg="black")
        self.beadImXYResWgt.grid(row=2, column=1, sticky="w")
        # Label(text="Resolution Z(nm/pixel)").grid(row = 5,column = 1)
        self.beadImZResWgt = Entry(f2, width=15, bg="white", fg="black")
        self.beadImZResWgt.grid(row=2, column=2, sticky="w")
        # setting default values
        self.beadSizeWgt.insert(0, str(200))
        self.beadImXYResWgt.insert(0, str(22))
        self.beadImZResWgt.insert(0, str(100))

        Label(
            f2,
            text="3. Run PSF calculation with desired number of iterations",
            font="Helvetica 10 bold",
        ).grid(
            row=3, column=0, columnspan=2, sticky="w"
        )  # blanc insert

        frameDeconPSFTypeSelect = Frame(f2)
        self.deconPSFType = StringVar()
        Label(frameDeconPSFTypeSelect, width=21, text="Deconvolution method:").pack(
            side=LEFT, padx=2, pady=2
        )
        deconPSFSelect = ttk.Combobox(
            frameDeconPSFTypeSelect,
            textvariable = self.deconPSFType,
            values = list( self.deconMethodsDict.keys() ),
            state="readonly",
        )
        deconPSFSelect.current(0)
        deconPSFSelect.pack(side=LEFT, padx=2, pady=2)
        self.deconProgBar = ttk.Progressbar(
            frameDeconPSFTypeSelect,
            orient = 'horizontal',
            mode = 'determinate',
            length = 100
            )
        self.deconProgBar.pack(side=LEFT, padx=2, pady=2)
        frameDeconPSFTypeSelect.grid(row=4, column = 0, columnspan=2,sticky="w")

        frameIterNumberInput = Frame(f2)
        Label(frameIterNumberInput, width=21, text="Iteration number:").pack(
            side=LEFT, padx=2, pady=2
        )
        self.deconIterNumPSF = Entry(frameIterNumberInput,width=5, bg="white", fg="black")
        self.deconIterNumPSF.pack( side=LEFT, padx=2, pady=2 )
        # setting default value
        self.deconIterNumPSF.insert(0, str(5))

        Label(frameIterNumberInput, width=15,  text="Regularization:").pack(
            side=LEFT, padx=2, pady=2
        )
        self.deconRegCoefPSF = Entry(frameIterNumberInput, width=10, bg="white", fg="black")
        self.deconRegCoefPSF.pack( side=LEFT, padx=2, pady=2 )
        # setting default value
        self.deconRegCoefPSF.insert(0, str(0.0001))
        frameIterNumberInput.grid(row=5, column = 0,columnspan=2,sticky="w")
        Button(f2, text="Calculate PSF", width=12, command=self.CalculatePSF).grid(
            row=4, column=2, padx=2, pady=2 
        )

        Button(f2, text="Save PSF as tiff", width=12, command=self.SavePSFSingle).grid(
            row=5, column=2, padx=2, pady=2 
        )

        Separator(f2, orient="horizontal").grid(
            row=6, column=0, ipadx=200, pady=10, columnspan=3
        )
        f2.grid(column=1, row=2, sticky="WENS")

        f3 = Frame(self)
        Label(f3, text=" ").grid(row=1, column=2)
        Label(f3, text="Deconvolve Image with PSF:", font="Helvetica 14 bold").grid(
            row=0, column=0, columnspan=2
        )
        Label(
            f3, text="1. Load Image tiff stack from file ", font="Helvetica 10 bold"
        ).grid(row=2, column=0, columnspan = 2, sticky="w")
        f3ButtonEntryFrame1 = Frame(f3) 
        Button(f3ButtonEntryFrame1, text="Load  Image", width=10, command=self.LoadPhotoImageFile).pack(side=LEFT, padx=10)
        self.EntryImageParam = Entry( f3ButtonEntryFrame1, width = 60 )
        self.EntryImageParam.insert( 0,"No Image Loaded" )
        self.EntryImageParam.configure( state="readonly" )
        self.EntryImageParam.pack(side=LEFT)
        f3ButtonEntryFrame1.grid(row=3, column=0,columnspan=3)
        Label(
            f3, text="2. Load PSF tiff stack from file ", font="Helvetica 10 bold"
        ).grid( row = 4, column = 0, sticky = "w" )
        f3ButtonEntryFrame2 = Frame(f3) 
        Button(f3ButtonEntryFrame2, text="Load PSF", width=10, command=self.LoadPSFImageFile).pack(side=LEFT, padx=10)
        self.EntryPSFParam = Entry(f3ButtonEntryFrame2, width = 60)
        self.EntryPSFParam.insert(0,"No PSF Loaded")
        self.EntryPSFParam.configure(state = "readonly")
        self.EntryPSFParam.pack(side=LEFT)
        f3ButtonEntryFrame2.grid(row=5, column=0,columnspan=3)

        Label(f3, text="3. Run deconvolution ", font="Helvetica 10 bold").grid(
            row=6, column=0, sticky="w"
        )

        f3_1 = Frame(f3)
        self.deconImageType = StringVar()
        Label(f3_1, width=21, text="Deconvolution method:").pack(
            side=LEFT, padx=2, pady=2
        )
        deconImageSelect = ttk.Combobox(
            f3_1,
            textvariable = self.deconImageType,
            values = list( self.deconMethodsDict.keys() ),
            state="readonly",
        )
        deconImageSelect.current(0)
        deconImageSelect.pack(side=LEFT, padx=2, pady=2)
        self.deconProgBarImage = ttk.Progressbar(
            f3_1,
            orient = 'horizontal',
            mode = 'determinate',
            length = 100
            )
        self.deconProgBarImage.pack(side=LEFT, padx=2, pady=2)
        f3_1.grid(row=7, column = 0, columnspan=2,sticky="w")

        f3_2 = Frame(f3)
        Label(f3_2, width=21, text="Iteration number:").pack(
            side=LEFT, padx=2, pady=2
        )
        self.deconIterNumImage = Entry(f3_2,width=5, bg="white", fg="black")
        self.deconIterNumImage.pack( side=LEFT, padx=2, pady=2 )
        # setting default value
        self.deconIterNumImage.insert(0, str(5))

        Label(f3_2, width=15,  text="Regularization:").pack(
            side=LEFT, padx=2, pady=2
        )
        self.deconRegCoefImage = Entry(f3_2, width=10, bg="white", fg="black")
        self.deconRegCoefImage.pack( side=LEFT, padx=2, pady=2 )
        # setting default value
        self.deconRegCoefImage.insert(0, str(0.0001))
        f3_2.grid(row=8, column = 0,columnspan=2,sticky="w")

        Button(
            f3, text = "Deconvolve", width=10, command = self.DeconvolveIt
        ).grid(row = 7, column = 2, padx = 2, pady = 2)
        Button(
            f3, text = "Save image", width=10, command = self.SaveDeconvImgSingle
        ).grid(row = 8, column = 2, padx = 2, pady = 2)
        Separator(f3, orient="horizontal").grid(
            row = 9, column = 0, ipadx = 200, padx = 30, pady = 10, columnspan = 3 
        )
        Button(f3, text="Close", command=self.CloseWindow).grid(row = 10, column = 1)
        f3.grid(row = 3, column = 1, sticky="WENS")

        Label(self, text="").grid(row = 1, column = 4)  # blanc insert

        self.cnvImg = Canvas(self, width = 180, height = 450, bg = "white")
        self.cnvImg.grid(row = 1, column = 5, rowspan = 10, sticky = (N, E, S, W))
        self.cnvPSF = Canvas(self, width = 180, height = 450, bg = "white")
        self.cnvPSF.grid(row = 1, column = 6, rowspan = 10, sticky = (N, E, S, W))
        self.cnvDecon = Canvas(self, width = 180, height = 450, bg = "white")
        self.cnvDecon.grid(row = 1, column = 7, rowspan = 10, sticky = (N, E, S, W))

        Label(self, text = "").grid(row = 13, column = 6)  # blanc insert

    def CloseWindow(self):
        """Closing window and clear tmp files"""
        # Checking existance of self.imgBeadsRaw.close()
        if askokcancel("Close", "Close Deconvolution Widget?"):
            self.destroy()


    def BlurImage(self, bead):
        """
        Blur bead with gauss
        """
        bead = gaussian_filter(bead, sigma=1)
        return bead

    def UpscaleImage_Zaxis(self, bead, plotPreview=False):
        """Upscale along Z axis of a given bead"""
        # теперь разбрасываем бид по отдельным массивам .
        zcoord = np.zeros(bead.shape[0])
        xcoord = np.zeros(bead.shape[1])
        ycoord = np.zeros(bead.shape[2])
        zcoordR = np.zeros(
            bead.shape[1]
        )  # shape of rescaled bead in Z dimension  - same as x shape
        #            bead = bead/np.amax(bead)*255.0 # normalize bead intensity
        maxcoords = np.unravel_index(np.argmax(bead, axis=None), bead.shape)
        #            print("maxcoords:",maxcoords)

        zcoord = np.arange(bead.shape[0]) * self.beadVoxelSize[0]
        xcoord = np.arange(bead.shape[1]) * self.beadVoxelSize[1]
        ycoord = np.arange(bead.shape[2]) * self.beadVoxelSize[2]
        # shift to compensate rescale move relative to center
        #            shift = (bead.shape[0] * self.beadVoxelSize[0] - bead.shape[1] * self.beadVoxelSize[1]) * 0.5
        # fixed shift now depends on center of the bead
        shift = (
            maxcoords[0] * self.beadVoxelSize[0]
            - bead.shape[1] * self.beadVoxelSize[1] * 0.5
        )
        zcoordR = shift + np.arange(bead.shape[1]) * self.beadVoxelSize[1]
        interp_fun = RegularGridInterpolator((zcoord, xcoord, ycoord), bead)

        pts = np.array(list(itertools.product(zcoordR, xcoord, ycoord)))
        pts_ID = list(
            itertools.product(
                np.arange(bead.shape[1]),
                np.arange(bead.shape[1]),
                np.arange(bead.shape[1]),
            )
        )
        ptsInterp = interp_fun(pts)
        beadInterp = np.ndarray((bead.shape[1], bead.shape[1], bead.shape[1]))
        for pID, p_ijk in enumerate(pts_ID):
            beadInterp[p_ijk[0], p_ijk[1], p_ijk[2]] = ptsInterp[pID]
        self.__upscaledBead = np.ndarray((bead.shape[1], bead.shape[1], bead.shape[1]))
        self.__upscaledBead = beadInterp
        if plotPreview == True:  # draw 3 projections of bead
            figUpsc, figUpscAxs = plt.subplots(3, 1, sharex=False, figsize=(2, 6))
            figUpsc.suptitle("Image preview")
            figUpscAxs[0].pcolormesh(
                beadInterp[beadInterp.shape[0] // 2, :, :], cmap=cm.jet
            )
            figUpscAxs[1].pcolormesh(
                beadInterp[:, beadInterp.shape[1] // 2, :], cmap=cm.jet
            )
            figUpscAxs[2].pcolormesh(
                beadInterp[:, :, beadInterp.shape[2] // 2], cmap=cm.jet
            )

            newWin = Toplevel(self)
            newWin.geometry("200x600")
            newWin.title("Image ")
            cnvFigUpsc = Canvas(newWin, width=200, height=600, bg="white")
            cnvFigUpsc.pack(side=TOP, fill=BOTH, expand=True)
            FigureCanvasTkAgg(figUpsc, cnvFigUpsc).get_tk_widget().pack(
                side=TOP, fill=BOTH, expand=True
            )

        return beadInterp


    def GetVoxelDialog(self, text = ""):
        """
        Create dialog and return list of values
        """
        voxelStr = askstring("Voxel Dialog", text)
        return [float(a) for a in voxelStr.split(",")]

    def LoadPhotoImageFile(self):
        """
        Loading raw photo from the microscope for deconvolution.
        Photo may be one multiframe TIFF of set of single frame TIFF files
        """

        fileList = askopenfilenames(title="Load Photo")
        print(fileList, type(fileList), len(fileList))
# new file load 
        try:
            self.img = ImageRaw(fileList)
        except ValueError as vE:
            if vE.args[1] == "voxel_problem":
                try:
                    tmpVoxel = self.GetVoxelDialog("Enter voxel size as z,x,y in \u03BCm")
                    self.img = ImageRaw(fileList, tmpVoxel)
                except ValueError as vE1:
                    print(vE1.args[0])
                    return
            elif vE.args[1] == "data_problem":
                print(vE.args[0])
                return
            else:
                print("Unknown problem while loading file.")
                return
        self.img.ShowClassInfo()

        # self.img.imArray = self.BlurImage(self.img.imArray)
        self.figIMG_canvas_agg = FigureCanvasTkFrom3DArray(self.img.imArray, self.cnvImg, plotName = "Image")
        self.figIMG_canvas_agg.get_tk_widget().grid(
            row=1, column=5, rowspan=10, sticky=(N, E, S, W)
        )
        self.EntryImageParam.configure( state="normal" )
        self.EntryImageParam.delete(0,END)
        self.EntryImageParam.insert( 0,self.img.GetImageInfoStr(output = "full") )
        self.EntryImageParam.configure( state="readonly" )
        
    #        self.imArr1 = self.UpscaleImage_Zaxis(self.imArr1,False)


    def LoadBeadImageFile(self):
        """
        Loading raw bead photo from file 
        """
        fnames = askopenfilenames(title="Select tiff image")

        try:
            self.imgBeadAvr = ImageRaw(fnames)
        except ValueError as vE:
            if vE.args[1] == "voxel_problem":
                try:
                    tmpVoxel = self.GetVoxelDialog("Enter voxel size as z,x,y in \u03BCm")
                    self.imgBeadAvr = ImageRaw(fnames, tmpVoxel)
                except ValueError as vE1:
                    print(vE1.args[0])
                    return
            elif vE.args[1] == "data_problem":
                print(vE.args[0])
                return
            else:
                print("Unknown problem while loading file.")
                return
        self.imgBeadAvr.ShowClassInfo()

        self.imgBeadRaw = self.imgBeadAvr.imArray

        # setting voxel values in GUI
        self.beadImXYResWgt.delete(0,END)
        self.beadImXYResWgt.insert(0, str(self.imgBeadAvr.voxel["X"] * 1000) )
        self.beadImZResWgt.delete(0,END)
        self.beadImZResWgt.insert(0, str(self.imgBeadAvr.voxel["Z"] * 1000) )
        self.beadVoxelSize[0] = self.imgBeadAvr.voxel["Z"]       
        self.beadVoxelSize[1] = self.imgBeadAvr.voxel["Y"]       
        self.beadVoxelSize[2] = self.imgBeadAvr.voxel["X"]
        
        # setting info about loaded file
        self.beadImgPathW.configure( state="normal" )
        self.beadImgPathW.delete(0,END)
        self.beadImgPathW.insert( 0, self.imgBeadAvr.GetImageInfoStr(output = "full") )
        self.beadImgPathW.configure( state="readonly" )

        self.figIMG_canvas_agg = FigureCanvasTkFrom3DArray(self.imgBeadRaw, self.cnvImg, "Bead")
        self.figIMG_canvas_agg.get_tk_widget().grid(
            row=1, column=5, rowspan=10, sticky=(N, E, S, W)
        )



    def LoadCompareImageFile(self):
        """Loading raw bead photo from file at self.beadImgPath"""
        beadCompPath = askopenfilename(title="Load Beads Photo")
        try:
            self.imgBeadComp = fio.ReadTiffStackFile(beadCompPath)
        except Exception as exc:
            showerror("Load compare image: Error", "Can't read file.")
            print(exc)
            return

    def CenteringImageInt(self):
        """Centering image array by intensity"""
        if not hasattr(self, "imgBeadRaw"):
            showerror("Error. No image loaded!")
            return
        try:
            #                imgBeadRaw = imtrans.CenterImageIntensity(self.imgBeadRaw)
            # FIXME: центровка работает как то странно. надо проверить и поправить.
            self.imgBeadRaw = imtrans.ShiftWithPadding(self.imgBeadRaw)

            self.figIMG_canvas_agg = FigureCanvasTkFrom3DArray(self.imgBeadRaw, self.cnvImg, plotName="Raw Bead")
            self.figIMG_canvas_agg.get_tk_widget().grid(
                row=1, column=5, rowspan=10, sticky=(N, E, S, W)
            )
        except Exception as exc:
            showerror("centering error")
            print(exc)

    def CalculatePSF(self):
        txt_beadSizenm = self.beadSizeWgt.get()
        txt_resolutionXY = self.beadImXYResWgt.get()
        #txt_resolutionXY = self.voxel["X"]
        txt_resolutionZ = self.beadImZResWgt.get()
        #txt_resolutionZ = self.voxel["Z"]
        print(txt_beadSizenm, txt_resolutionXY, txt_resolutionZ)
        if not hasattr(self, "imgBeadRaw"):
            showerror("Error", "No bead image loaded.")
        elif txt_beadSizenm == "" or txt_resolutionXY == "" or txt_resolutionZ == "":
            showerror("Error", "Empty Bead size or resolution value.")
        elif txt_beadSizenm == "0" or txt_resolutionXY == "0" or txt_resolutionZ == "0":
            showerror("Error", "Zero Bead size or resolution value.")
        else:
            try:
                self.beadSizenm = float(txt_beadSizenm)
                self.resolutionXY = float(txt_resolutionXY)
                self.resolutionZ = float(txt_resolutionZ)
                self.beadSizepx = int(self.beadSizenm / self.resolutionXY / 2)
# sss               self.imArr1 = imtrans.PaddingImg(self.imgBeadRaw)
                self.imArr1 = self.imgBeadRaw
                print(
                    "shapes:",
                    self.imArr1.shape[0],
                    self.imArr1.shape[1],
                    self.imArr1.shape[2],
                )
                
                print("call DeconPSF")
                self.imgPSF = decon.DeconPSF(
                    self.imArr1, self.beadSizepx,
                    int( self.deconIterNumPSF.get() ),
                    self.deconMethodsDict[ self.deconPSFType.get() ],
                    float(self.deconRegCoefPSF.get()),
                    progBar=self.deconProgBar, parentWin=self
                )
            except Exception as exc:
                showerror("Error. Can't finish convolution properly. ",str(exc))
                return
            self.figPSF_canvas_agg = FigureCanvasTkFrom3DArray(self.imgPSF, self.cnvPSF, plotName = "PSF")
            self.figPSF_canvas_agg.get_tk_widget().grid(
                row=1, column=5, rowspan=10, sticky=(N, E, S, W)
            )

    def SavePSFMulti(self):
        """Save PSF array as single-page tiff files"""
        if hasattr(self, "imgPSF"):
            # txt_folder = self.folderPSFWgt.get()
            # txt_prefix = self.filePrfxPSFWgt.get()
            # if txt_prefix == '':
            txt_prefix = "EML_psf"
            # if txt_folder == '':
            dirId = -1
            while True:
                dirId += 1
                print(dirId)
                txt_folder = str(os.getcwd()) + "\\" + "PSF_folder_" + str(dirId)
                if not path.isdir(txt_folder):
                    print("Creating new  PSF folder")
                    os.mkdir(txt_folder)
                    break
            fio.SaveTiffFiles(self.imgPSF, txt_folder, txt_prefix)
            showinfo("PSF Files saved at:", txt_folder)


    def SavePSFSingle(self):
        """Save PSF array as single tiff"""
        if hasattr(self, "imgPSF"):
            self.SaveImage(self.imgPSF)


    def SaveDeconvImgSingle(self):
        """Save deconvolved image as multi-page tiff"""
        if hasattr(self, "imgDecon"):
            self.SaveImage(self.imgDecon)

    def SaveImage(self, imageArray:np.ndarray):
        """
        Save imageArray as multi-page tiff
        """
        filesMask = [('All Files', '*.*'), ('TIFF file', '*.tif')]
        fname = asksaveasfilename(title="Save PSF as",
            filetypes = filesMask,
            defaultextension = filesMask,
            initialfile = "new_psf.tif")
        try:
            tmpDict = dict(zip(self.voxelFields,self.beadVoxelSize))
            fio.SaveAsTiffStack_tag(imageArray, fname, outtype = "uint8", tagID = 270, tagString = json.dumps(tmpDict))
        except Exception as e:
            showerror("Can't save image as ", fname + "\n Exception: " + str(e))
            return
        showinfo("Image saved at:", fname)

    def LoadPSFImageFile(self):
        """
        Loading raw bead photo from file located at self.beadImgPath
        """
        fileList = askopenfilenames(title="Select PSF file")
        print(fileList, type(fileList), len(fileList))
        try:
            self.imagePSF = ImageRaw(fileList)
        except ValueError as vE:
            if vE.args[1] == "voxel_problem":
                try:
                    tmpVoxel = self.GetVoxelDialog("Enter voxel size as z,x,y in \u03BCm")
                    self.imagePSF = ImageRaw(fileList, tmpVoxel)
                except ValueError as vE1:
                    print(vE1.args[0])
                    return
            elif vE.args[1] == "data_problem":
                print(vE.args[0])
                return
            else:
                print("Unknown problem while loading file.")
                return
        self.imagePSF.ShowClassInfo()

        #self.imagePSF.imArray = self.BlurImage(self.imagePSF.imArray)
        self.figIMG_canvas_agg = FigureCanvasTkFrom3DArray(self.imagePSF.imArray, self.cnvPSF, plotName = "PSF")
        self.figIMG_canvas_agg.get_tk_widget().grid(
            row=1, column=5, rowspan=10, sticky=(N, E, S, W)
        )

        self.EntryPSFParam.configure( state="normal" )
        self.EntryPSFParam.delete(0,END)
        self.EntryPSFParam.insert( 0,self.imagePSF.GetImageInfoStr(output = "full") )
        self.EntryPSFParam.configure( state="readonly" )



    def DeconvolveIt(self):
        """Deconvolution of image with calculated PSF
        Calculation times on I7-11700k 20 iteration:
        3test_spheres - 100х100 - 38.9s / Phenom II 142s
        test_strings - 200х200  - 216.9s
        """
        doRescaleZ = True
        if doRescaleZ:
            rescaleCoef = self.imagePSF.voxel["Z"] / self.img.voxel["Z"] 
            try:
                kernell = zoom(self.imagePSF.imArray,[rescaleCoef, 1.0, 1.0])
                # self.imagePSF.RescaleZ(self.img.voxelSize[1])
            except Exception as e:
                print("rescale failed"+str(e))
                return
        start_time = time.time()
        try:
            self.imgDecon = decon.DeconImage(
                self.img.imArray, kernell,
                int( self.deconIterNumImage.get() ),
                self.deconMethodsDict[ self.deconImageType.get() ],
                float(self.deconRegCoefImage.get()),
                progBar=self.deconProgBarImage, parentWin=self
            )
        except Exception as e:
            print("Deconvolution failed. "+str(e))
            return
        print("Decon output shape:", self.imgDecon.shape)
        print("Deconvolution time: %s seconds " % (time.time() - start_time))
        self.figDec_canvas_agg = FigureCanvasTkFrom3DArray(self.imgDecon, self.cnvDecon, "Deconvolved")
        self.figDec_canvas_agg.get_tk_widget().grid(
            row=1, column=6, rowspan=10, sticky=(N, E, S, W)
        )

        # plotting XY on separate canvas
        figComp, ax = plt.subplots(1, 1, sharex=False, figsize=(1, 1))
        dN = self.imgDecon.shape[0]
        ax.pcolormesh(self.img.imArray[dN // 2, :, :], cmap=cm.jet)
        top = Toplevel(self)
        top.geometry("600x600")
        top.title("Initial image XY plane")
        cnvCompare = Canvas(top, width=590, height=590, bg="white")
        cnvCompare.pack(side=TOP, fill=BOTH, expand=True)
        FigureCanvasTkAgg(figComp, cnvCompare).get_tk_widget().pack(
            side=TOP, fill=BOTH, expand=True
        )

        # plotting XY on separate canvas
        figComp, ax = plt.subplots(1, 1, sharex=False, figsize=(1, 1))
        dN = self.imgDecon.shape[0]
        ax.pcolormesh(self.imgDecon[dN // 2, :, :], cmap=cm.jet)
        top = Toplevel(self)
        top.geometry("600x600")
        top.title("Deconvolved image XY plane")
        cnvCompare = Canvas(top, width=590, height=590, bg="white")
        cnvCompare.pack(side=TOP, fill=BOTH, expand=True)
        FigureCanvasTkAgg(figComp, cnvCompare).get_tk_widget().pack(
            side=TOP, fill=BOTH, expand=True
        )


if __name__ == "__main__":
    rootWin = DeconvolutionGUI(Tk())
    rootWin.mainloop()