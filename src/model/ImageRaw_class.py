import numpy as np
import itertools
from scipy.interpolate import RegularGridInterpolator
from PIL import Image
import json


class ImageRaw:
    """
    Class for image:
        attributes:
        self.imArray: np.ndarray - array of pixel intensities
        self.voxel: dict - voxel sizes in each dimension
        voxelSizeIn: List [z,y,x]
        imArrayIn: np.array[nz,ny,nx]
    """

    def __init__(
        self, fpath : str = None, voxelSizeIn : list = None, imArrayIn : np.ndarray = None
    ):
        self.imArray = None
        self.voxel = None #{"Z":0, "Y":0, "X":0}
        self.voxelSize = None # obsolete
        self.voxelFields = ("Z", "Y", "X") # obsolete

        if fpath is None:
            if imArrayIn is None:
                raise ValueError("No data recieved.","data_problem")
            else:
                if voxelSizeIn is None:
                    raise ValueError("No voxel recieved.","voxel_problem")
                else:
                    try:
                        self.SetArray(imArrayIn)
                    except:
                        raise ValueError("Can not set array from the argument.","data_problem")
                    try:
                        self.SetVoxel(voxelSizeIn)
                    except:
                        raise ValueError("Can not set voxel from the argument.","voxel_problem")
        else:
            if imArrayIn is None:
                imArrayFile,tagString = self.LoadImageFile(fpath, 270)
                if tagString == "" :
                    if voxelSizeIn is None:
                        raise ValueError("No voxel recieved from file or as argument","voxel_problem")
                    else:
                        try:
                            self.SetArray(imArrayFile)
                        except:
                            raise ValueError("Can not set array from file.","data_problem")
                        try:
                            self.SetVoxel(voxelSizeIn)
                        except:
                            raise ValueError("Can not set voxel from argument.","voxel_problem")
                else:
                    if voxelSizeIn is None:
                        try:
                            self.SetArray(imArrayFile)
                        except:
                            raise ValueError("Can not set array from file.","data_problem")
                        try:
                            try:
                                voxelSizeIn = json.loads(tagString)
                            except :
                                raise ValueError("Can not convert tag. Check tag format.","voxel_problem")
                            self.SetVoxel( [voxelSizeIn["Z"], voxelSizeIn["X"], voxelSizeIn["Y"]] ) 
                        except:
                            raise ValueError("Can not set voxel from tag. Check tag format.","voxel_problem")
                    else:
                        try:
                            self.SetArray(imArrayFile)
                        except:
                            raise ValueError("Can not set array from file.","data_problem")
                        try:
                            self.SetVoxel(voxelSizeIn)
                        except:
                            raise ValueError("Can not set voxel from argument.","voxel_problem")
            else:
                raise ValueError("Only one source of data for pixel values allowed","data_problem")

            self.path =  fpath[0] 


    # methods

    def LoadImageFile(self, fileNameList: tuple, tagID = 270):
        """
        Function LoadImageFile() reads tiff stack from file name list
            Input:
                fileName - path to file
                tagID - tag index (default 270 - file info)
            Returns tuple : (imgArray , tag)
                imgArray : ndarray  - array of pixel values in grayscale
                tag : str - tag string for tagID
        """
        
        if len(fileNameList) < 1:
            raise ValueError("Empty file name list")
        elif len(fileNameList) == 1:

            try:
                with Image.open(fileNameList[0]) as image_tiff:
                    ncols, nrows = image_tiff.size
                    nlayers = image_tiff.n_frames
                    imgArray = np.ndarray([nlayers, nrows, ncols]) # Z,Y,X
                    if image_tiff.mode == "I" or image_tiff.mode == "L":
                        for i in range(nlayers):
                            image_tiff.seek(i)
                            imgArray[i, :, :] = np.array(image_tiff)
                    elif image_tiff.mode == "RGB":
                        for i in range(nlayers):
                            image_tiff.seek(i)
                            image_tiff.getdata()
                            r, g, b = image_tiff.split()
                            ra = np.array(r)
                            ga = np.array(g)
                            ba = np.array(b)
                            #recalculate greyscale intensity from rgb values
                            grayImgArr = 0.299 * ra + 0.587 * ga + 0.114 * ba
                            imgArray[i, :, :] = grayImgArr
                    else:
                        raise ValueError( "Unsupported tiff file mode: {}".format( str(image_tiff.mode) ) )          
            except :
                raise FileNotFoundError("Can't load file: {} ".format(fileNameList[0]) )
        else:
            # multi file load
            try:
                with Image.open(fileNameList[0]) as image_preread:
                    # print("color_mode:", image_preread.mode, ".......", end=" ")
                    nlayers = len(fileNameList)
                    ncols, nrows = image_preread.size
                    imgArray = np.ndarray([nlayers, nrows, ncols])
                    # checking file color mode and convert to grayscale
                    if image_preread.mode == "RGB":
                        # convert to Grayscale
                        for i, fileName in enumerate(fileNameList):
                            try: 
                                with Image.open(fileName) as image_tiff:
                                    if image_tiff.n_frames != 1:
                                        raise ValueError( "Not singleframe tif file in list of files: {}".format( fileName ) )
                                    image_tiff.getdata()
                                    r, g, b = image_tiff.split()

                            except :
                                raise FileNotFoundError( "Can't load file: {} ".format( fileName ) )
                            ra = np.array(r)
                            ga = np.array(g)
                            ba = np.array(b)
                            grayImgArr = 0.299 * ra + 0.587 * ga + 0.114 * ba
                            imgArray[i, :, :] = grayImgArr
                    elif image_preread.mode == "I" or image_preread.mode == "L":
                        for i, fileName in enumerate(fileNameList):
                            try:
                                with Image.open(fileName) as imageFile:
                                    imgArray[i, :, :] = np.array(imageFile)
                            except:
                                raise FileNotFoundError("Can't load file: {} ".format( fileName ))
                    else:
                        raise ValueError( "Unsupported tiff file mode: {}".format( str(image_tiff.mode) ) )

            except:
                raise FileNotFoundError("Can't load file: {} ".format(fileNameList[0]) )
        try:
            return imgArray, image_tiff.tag[tagID][0]
        except:
            return imgArray, ""

    def SetArray(self, newArray: np.ndarray):
        """
        Setting pixel array values
        """
        if newArray is None or len(newArray.shape) > 3 :
            raise ValueError("Wrong array Value.")
        # fixing possible array elements values issues
        newArray[np.isnan(newArray)] = 0  # replace NaN with 0
        newArray.clip(0)                  # replace negative with 0
        self.imArray = newArray

    def SetVoxel(self, newVoxel):
        """
            Setting voxel with check
        """
        if newVoxel is None or len(newVoxel) != 3 or np.amin(newVoxel) <= 0:
            raise ValueError("Wrong Voxel Value.","bad_voxel_value")
        else:
            self.voxelSize = newVoxel
            self.voxel = dict(zip(self.voxelFields, newVoxel))

    def RescaleZ(self, newZVoxelSize):
        """
            Rescale over z. newZVoxelSize in micrometers
        """
        # теперь разбрасываем бид по отдельным массивам .
        oldShape = self.imArray.shape

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

    def GetImageInfoStr(self, output = None):
        """
            Return string with array and voxel parameters.
        """
        if output == "full":
            return "Image size(z,y,x)px: " + str(self.imArray.shape) + "  Voxel(\u03BCm): " + str(list(self.voxel.values()))
        else:
            return str( self.imArray.shape ) + str(list(self.voxel.values()))

    def ShowClassInfo( self ):
        """
            Prints class attributes. 
        """
        print( " ImageClassInfo: " )
        print( " path: ", self.path )
        print( " voxel(micrometres): ", self.voxelSize )
        print( " image shape: ", self.imArray.shape )

    def SaveAsTiff(self, filename="img", outtype="uint8"):
        """
        Save Image as TIFF file
        Input: filename - path to file, including file name
               outtype - bit type for output
        """
        print("Trying to save TIFF file", outtype)
        try:
            tagID = 270
            # strVoxel = ';'.join(str(s) for s in self.voxelSize)
            strVoxel = json.dumps(self.voxel)
            imlist = []
            for tmp in self.imArray:
                imlist.append(Image.fromarray(tmp.astype(outtype)))
            #imlist[0].tag[270] = strVoxel
            imlist[0].save(
                filename, tiffinfo={tagID:strVoxel}, save_all=True, append_images=imlist[1:]
            )
        except:
            raise IOError("Cannot save file "+filename,"file_not_saved")
        print("File saved in ", filename)


if __name__ == "__main__":
    pass        
