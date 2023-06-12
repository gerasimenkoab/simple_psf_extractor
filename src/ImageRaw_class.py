import numpy as np
import itertools
from scipy.interpolate import interpn
from scipy.interpolate import RegularGridInterpolator
from tkinter import *
from tkinter.simpledialog import askstring
from PIL import Image
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.cm as cm
import json

class ImageRaw:
    """Class for image storage."""

    def __init__(
        self, fpath = "", voxelSizeIn=None, imArrayIn = None
    ):
        if fpath == "" and imArrayIn != None :
            self.imArray = imArrayIn
            self.SetVoxel(voxelSizeIn)  # microscope voxel size(z,x,y) in micrometres (resolution=micrometre/pixel)
            self.voxel = {"Z":voxelSizeIn[0],"X":voxelSizeIn[1],"Y":voxelSizeIn[2]}
        elif fpath == "" and imArrayIn == None:
            raise Exception("Can not initialize Image Object.")
        else:
            try:
                self.imArray, tmpStr = self.LoadImageFile(fpath, 270)
                if tmpStr == "" :
                    voxelStr = askstring("Voxel Dialog", "Enter voxel size as z,x,y in \u03BCm")
                    voxelIn = [float(a) for a in voxelStr.split(",")]
                    self.SetVoxel(voxelIn) 
                else:
                    voxelIn = json.loads(tmpStr)
                    self.SetVoxel( [voxelIn["Z"], voxelIn["X"], voxelIn["Y"]] ) 
            except Exception as e:
                print(str(e))
                raise
        self.path =  fpath 
        self.voxelFields = "Z", "X", "Y"
        self.voxelSizeEntries = {}

        # fixing possible array value issues
        self.imArray[np.isnan(self.imArray)] = 0  # replace NaN with 0
        self.imArray.clip(0)                      # replace negative with 0

    # methods

    def LoadImageFile(self, fileName = "img", tagID = 270):
        """
        Function LoadImageFile() reads tiff stack from file and return np.array
        Input:
            fileName - path to file
            fileInfo - if true then read tag string and return it
            tagID - tag index
        Returns:
            imgArray : ndarray
            image_tiff.tag[tagID][0] : str
        """
        print("Loading Image from tiff stack file..... ", end=" ")
        try:
            image_tiff = Image.open(fileName)
        except Exception as e:
            print( str(e) )
            raise FileNotFoundError
            #return None,""
        # meta_dict = {TAGS[key]:image_tiff.tag[key] for key in image_tiff.tag}
        # print(meta_dict)
        
        ncols, nrows = image_tiff.size
        nlayers = image_tiff.n_frames
        imgArray = np.ndarray([nlayers, nrows, ncols])
        for i in range(nlayers):
            image_tiff.seek(i)
            imgArray[i, :, :] = np.array(image_tiff)
        print("Done!")
        try:
            return imgArray, image_tiff.tag[tagID][0]
        except:
            return imgArray, ""

    def ShowClassInfo( self, plotPreview = False ):
        """
            Prints class attributes. 
        """
        print( " ImageClassInfo: " )
        print( " path: ", self.path )
        print( " voxel(micrometres): ", self.voxelSize )
        print( " image shape: ", self.imArray.shape )
        if plotPreview == True:  # draw 3 projections of bead
            figUpsc, figUpscAxs = plt.subplots( 3, 1, sharex=False, figsize=(2, 6) )
            figUpsc.suptitle( "Image preview" )
            figUpscAxs[0].pcolormesh(
                self.imArray[self.imArray.shape[0] // 2, :, :], cmap=cm.jet
            )
            figUpscAxs[1].pcolormesh(
                self.imArray[:, self.imArray.shape[1] // 2, :], cmap=cm.jet
            )
            figUpscAxs[2].pcolormesh(
                self.imArray[:, :, self.imArray.shape[2] // 2], cmap=cm.jet
            )
            newWin = Toplevel(self)
            newWin.geometry( "200x600" )
            newWin.title( "Image " )
            cnvFigUpsc = Canvas( newWin, width = 200, height = 600, bg = "white" )
            cnvFigUpsc.pack( side = TOP, fill = BOTH, expand = True )
            FigureCanvasTkAgg( figUpsc, cnvFigUpsc ).get_tk_widget().pack(
                side = TOP, fill = BOTH, expand = True
            )

    def CheckVoxel(self, voxel):
        """
            Checking if voxel empty,wrong length or wrong values. All good return True
        """
        if len(voxel) != 3 or np.amin(voxel) <= 0:
            raise Exception("Voxel Value Error.")
        return True

    def SetVoxel(self, newVoxel):
        """
            Setting objects voxel
        """
        if newVoxel == None:
            raise Exception("Voxel Value Error.")
        if self.CheckVoxel(newVoxel):
            try:
                self.voxelSize = newVoxel
            except:
                print("Can't assign new voxel.")
                return False
        else:
            print("Something wrong with new voxel.")
            return False
        return True

    def RescaleZ(self, newZVoxelSize):
        """
            Rescale over z. newZVoxelSize in micrometers
        """
        # теперь разбрасываем бид по отдельным массивам .
        oldShape = self.imArray.shape
        #        print("old shape:",oldShape)
        #        print("newshape:",newShape)
        # zcoord = np.zeros(oldShape[0])
        # xcoord = np.zeros(oldShape[1])
        # ycoord = np.zeros(oldShape[2])
        # zcoordR = np.zeros(shapeZ) # shape of rescaled bead in Z dimension  - same as x shape
        #            bead = bead/np.amax(bead)*255.0 # normalize bead intensity
        #        maxcoords = np.unravel_index(np.argmax(bead, axis=None), bead.shape)
        #            print("maxcoords:",maxcoords)

        zcoord = np.arange(oldShape[0]) * self.voxelSize[0]
        xcoord = np.arange(oldShape[1]) * self.voxelSize[1]
        ycoord = np.arange(oldShape[2]) * self.voxelSize[2]
        shapeZ = int(zcoord[oldShape[0] - 1] / newZVoxelSize)
        print(
            "voxel size, oldshape, shapeZ :",
            self.voxelSize[0],
            oldShape[0],
            (shapeZ),
        )
        zcoordR = np.arange(shapeZ) * newZVoxelSize
        #        print("zcoord:",zcoord,shapeZ)
        #        print("zcoordR:",zcoordR)
        interp_fun = RegularGridInterpolator((zcoord, xcoord, ycoord), self.imArray)

        pts = np.array(list(itertools.product(zcoordR, xcoord, ycoord)))
        pts_ID = list(
            itertools.product(
                np.arange(shapeZ), np.arange(oldShape[1]), np.arange(oldShape[2])
            )
        )
        ptsInterp = interp_fun(pts)
        beadInterp = np.ndarray((shapeZ, oldShape[1], oldShape[2]))
        for pID, p_ijk in enumerate(pts_ID):
            beadInterp[p_ijk[0], p_ijk[1], p_ijk[2]] = ptsInterp[pID]
        self.imArray = beadInterp
        self.voxelSize[0] = newZVoxelSize

    def GetImageParam(self, output = "full"):
        """
            Return string with array and voxel parameters.
        """
        if output == "full":
            return "Image size(z,y,x)px: " + str(self.imArray.shape) + "  Voxel(\u03BCm): " + str(self.voxelSize)
        elif output == "dimensions":
            return str( self.imArray.shape ) + str( self.voxelSize )
        else:
            return None
        
    def SaveAsTiffSingle(self, filename="img", outtype="uint8"):
        """
        Save Image as TIFF file
        Input: filename - path to file, including file name
               outtype - bit type for output
        """
        print("Trying to save TIFF file", outtype)
        tagID = 270
        strVoxel = ';'.join(str(s) for s in self.voxelSize)
        imlist = []
        for tmp in self.imArray:
            imlist.append(Image.fromarray(tmp.astype(outtype)))
        #imlist[0].tag[270] = strVoxel
        imlist[0].save(
            filename, tiffinfo={tagID:strVoxel}, save_all=True, append_images=imlist[1:]
        )
        print("File saved in ", filename)


if __name__ == "__main__":
    pass
