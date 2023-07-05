import numpy as np
import os
from scipy.ndimage import gaussian_filter, median_filter
from ImageRaw_class import ImageRaw

class model:
    def __init__(self):
        self._mainImage = ImageRaw([0.2,0.089,0.089],np.zeros((10,200,200)))
        self._averageBead = None
        self._beadCoords = []  # Coordinates of beads on the canvas
        self._extractedBeads = []
        self._beadDiameter = 0.2
        self._selectionFrameHalf = 18 

    @property
    def mainImage(self):
        return self._mainImage

    @mainImage.setter
    def mainImage( self, fname = None, voxel = None, array = None ):
        try:
            self._mainImage = ImageRaw(fname,voxel,array)
            self._averageBead = None
        except ValueError as vE:
            raise(vE.args)
    
    @property
    def averageBead(self):
        return self._averageBead
    
    @averageBead.setter
    def averageBead(self, value: ImageRaw):
        self._averageBead = value

    @property
    def beadCoords(self):
        return self._beadCoords
    
    @beadCoords.setter
    def beadCoords(self, coordsList):
        self._beadCoords = coordsList

    @property
    def beadDiameter(self):
        return self._beadDiameter

    @beadDiameter.setter
    def beadDiameter(self,value):
        if value > 0 and type(value) == int or float:
            self._beadDiameter = value
        else:
            raise ValueError("Wrong bead diameter value","beadDiameter_incorrect")
    
    @property
    def selectionFrameHalf(self):
        return self._selectionFrameHalf

    @selectionFrameHalf.setter
    def selectionFrameHalf(self, value):
        if value > 0 and type(value) == int or float:
            self._selectionFrameHalf = value
        else:
            raise ValueError("Wrong selection frame size value","selectionFrameHalf_incorrect")

    def BeadCoordsAdd(self, x, y):
        """Append mouse event coordinates to global list. Center is adjusted according to max intensity."""
        self._beadCoords.append([x, y])

    def LastBeadCooordsRemove(self):
        """Removes the last bead in the list"""
        self._beadCoords.pop()

    def BeadCoordsClear(self):
        """Clears all bead marks"""
        self._beadCoords = []

    def LocateFrameMAxIntensity3D(self, xi, yi):
        """Locate point with maximum intensity in current 3d array.
        In: 
           xi - approximate bead coordinate X
           yi - approximate bead coordinate Y
        Out: 
            coordinates of point with max intensity within frame
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
        sample = self._mainImage.imArray[:, bound1:bound2, bound3:bound4]
        coords = np.unravel_index(np.argmax(sample, axis=None), sample.shape)
        return coords[2] + bound3, coords[1] + bound1

 
    def SetVoxelSize(self, newVoxelSizeList):
        """Bead voxel size change"""
        try:
            self._mainImage.SetVoxel(newVoxelSizeList)
        except ValueError as vErr:
            raise ValueError(vErr.args)




    def ExtractBeads(self):
        """Extracting bead stacks from picture set and centering them"""
        d = self._selectionFrameHalf
        print(self.imgCnvArr.shape)
        voxel = list( self._mainImage.voxel.values() )
        for idx, i in enumerate(self.beadCoords):
            bound3 = int(i[0] - d)
            bound4 = int(i[0] + d)
            bound1 = int(i[1] - d)
            bound2 = int(i[1] + d)
            elem = self._mainImage.imArray[:, bound1:bound2, bound3:bound4]
            # shifting array max intesity toward center along Z axis
            iMax = np.unravel_index(np.argmax(elem, axis=None), elem.shape)
            zc = int(elem.shape[0] / 2)
            shift = zc - iMax[0]
            elem = np.roll(elem, shift=shift, axis=0)
            iMax = np.unravel_index(np.argmax(elem, axis=None), elem.shape)
            self._extractedBeads.append( ImageRaw(voxel, elem) )

    def SaveSelectedBeads(self, txt_folder_enquiry, txt_prefix = "", tiffBit = "uint8"):
        """Save selected beads as multi-page tiffs as is."""
        if self._extractedBeads != None:
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
            for idx, bead in enumerate(self._extractedBeads):
                fname = txt_folder + "/" + str(idx).zfill(2) + ".tif"
                bead.SaveAsTiff(fname, outtype = tiffBit)
        else:
            raise ValueError("No beads extracted","empty_beads_list")
        
    def BlurBead(self, bead : ImageRaw, blurType):
        """
        Blur bead with selected filter
        In:
            bead : ImageRaw  - image to blur
        Out:
            bead : ImageRaw - blured image
        """

        if blurType == "gauss":
            bead = gaussian_filter(bead.imArray, sigma=1)
        elif blurType == "median":
            bead = median_filter(bead.imArray, size=3)
        return bead

    def BeadsArithmeticMean(self):
        #            print("blurtype", self.blurApplyType.get(), "rescale Z", self.doRescaleOverZ.get() )
        if self._extractedBeads == None:
            raise ValueError("No beads extracted","empty_beads_list")
        else:
            try:
                sumArray = np.zeros( self._extractedBeads[0].imArray.shape )
                for bead in self._extractedBeads:
                    sumArray = sumArray + bead.imArray
                sumArray = sumArray / len( self._extractedBeads )
                self.avrageBead = ImageRaw( list(self._extractedBeads[0].voxel.values()), sumArray )
            except:
                raise RuntimeError("Failed to average beads")

    def SaveAverageBead(self,fname, tiffBit ="uint8"):
        """
        Save averaged bead to file
        In:
            fname : str - path including file name
        """
        if self._averageBead == None:
            raise ValueError("Average bead was not created.", "averageBead_not_exist")
        try:
            self._averageBead.SaveAsTiff(fname)
        except IOError as e:
            raise IOError(e[0],e[1])
        
    def LoadManyBeads(self, fileList):
        """Loading many raw bead photos from files"""
        beadsList = []
        dimensions = []
        if len(fileList) < 1:
            raise ValueError("No bead files selected.","empty_file_list")
        else:
            fPath = fileList[0]
            newBead = ImageRaw(fPath)
            dimensions = newBead.imArray.shape
            beadsList.append(newBead)

            for fPath in fileList[1:]:
                try:
                    newBead = ImageRaw(fPath)
                    if dimensions == newBead.imArray.shape:
                        beadsList.append( newBead )
                    else:
                        raise ValueError( "Beads images of different size found", "bead_size_not_coincide" )
                except ValueError as vErr:
                    raise ValueError(vErr.args)
        return beadsList

    def AvrageManyBeads(self, fileList, fileSaveName):
        """
        Loading many same size bead files and calculate the arithmetic mean.
        Output: file with averaged bead.
        """
        try:
            beadsList = self.LoadManyBeads(fileList)
            sumArray = np.zeros(beadsList[0].imArray.shape)
            for bead in beadsList:
                sumArray = sumArray + bead.imArray
            sumArray = sumArray / len(beadsList)
            ImageRaw(list(beadsList[0].voxel.values()), sumArray).SaveAsTiff(fileSaveName)
        except:
            raise RuntimeError("Failed to average beads")
