import numpy as np
import itertools
from scipy.interpolate import RegularGridInterpolator
from PIL import Image
import json
import json


class Voxel:
    """
    Class for voxel:
        attributes:
        _voxelValues: List [z,y,x]
        _axisNames: Tuple ("Z", "Y", "X")
    """

    _voxelValues:list = None
    _axisNames:tuple = ("Z", "Y", "X")

    def __init__(self, voxelSizeIn: list = None):
        super().__init__()
        if voxelSizeIn is not None:
            self.Set(voxelSizeIn)

    def Set(self, newVoxel: list)->None:
        """
            Setting voxel with check
        """
        if newVoxel is None or len(newVoxel) != 3 or np.amin(newVoxel) <= 0:
            raise ValueError("Wrong Voxel Value.")
        else:
            self._voxelValues = newVoxel

    def Get(self)->list:
        """
            Getting list of voxel values
        """
        if self._voxelValues is None:
            raise ValueError("No voxel Value.")
        return self._voxelValues
    
    def SetToAxis(self, axisName:str, newValue:float)->None:
        """
            Setting voxel value by axis name
        """
        if newValue <= 0:
            raise ValueError("Wrong voxel value.")
        if axisName in self._axisNames:
            self._voxelValues[self._axisNames.index(axisName)] = newValue
        else:
            raise ValueError("Wrong axis name.")

    def GetFromAxis(self, axisName:str)->float:
        """
            Getting voxel value by axis name
        """
        if axisName in self._axisNames:
            return self._voxelValues[self._axisNames.index(axisName)]
        else:
            raise ValueError("Wrong axis name.")
        
    def GetDict(self)->dict:
        """
            Getting voxel as dict
        """
        return dict(zip(self._axisNames, self._voxelValues))

    def GetValuesStr(self)->str:
        """
            Getting voxel values list as string
        """
        return str(self._voxelValues)

    def GetVoxelJson(self)->str:
        """
            Getting voxel as json string
        """
        return json.dumps(dict(zip(self._axisNames, self._voxelValues)))

    def ShowInfo(self)->None:
        """
            Prints voxel parameters
        """
        print("Voxel size: ", self._voxelValues)

class IntensityValues:
    """
    Class for intensity values:
        attributes:
        self._pointIntensities: np.ndarray - array of pixel intensities
    """

    _pointIntensities: np.ndarray = None

    def __init__(self, pointIntensitiesIn: np.ndarray = None):
        super().__init__()
        if pointIntensitiesIn is not None:
            self.Set(pointIntensitiesIn)

    def Set(self, newArray: np.ndarray)->None:
        """
        Setting pixel array values
        """
        if newArray is None or len(newArray.shape) > 3:
            raise ValueError("Wrong array Value.")
        # fixing possible array elements values issues
        newArray[np.isnan(newArray)] = 0  # replace NaN with 0
        newArray.clip(0)  # replace negative with 0
        self._pointIntensities = newArray

    def SetWithoutCorrections(self, newArray: np.ndarray):
        """
        Setting pixel array values
        """
        if newArray is None or len(newArray.shape) > 3:
            raise ValueError("Wrong array Value.")
        self._pointIntensities = newArray


    def Get(self)->np.ndarray:
        """
            Getting pixel array values
        """
        if self._pointIntensities is None:
            raise ValueError("No array Value.")
        return self._pointIntensities
    
    def GetShape(self)->list:
        """
            Getting pixel array dimensions
        """
        if self._pointIntensities is None:
            raise ValueError("No array Value.")
        return self._pointIntensities.shape

    def ShowInfo(self)->None:
        """
            Prints array parameters
        """
        print("Array shape: ", self._pointIntensities.shape)
        print("Array min: ", np.amin(self._pointIntensities))
        print("Array max: ", np.amax(self._pointIntensities))
        print("Array mean: ", np.mean(self._pointIntensities))

class ImageRaw:
    """
    Class for image:
        attributes:
        self.intensities: np.ndarray - array of pixel intensities
        self.voxel: dict - voxel sizes in each dimension
        voxelSizeIn: List [z,y,x]
        imArrayIn: np.array[nz,ny,nx]
    """

    intensities = IntensityValues()
    voxel = Voxel() 
    #{"Z":0, "Y":0, "X":0}
    # voxelSize = None # obsolete
    # voxelFields = ("Z", "Y", "X") 

    def __init__(
        self, fpath : str = None, voxelSizeIn : list = None, intensitiesIn : np.ndarray = None
    ):
        # super().__init__()
        if fpath is None:
            if intensitiesIn is None:
                raise ValueError("No data recieved.","data_problem")
            else:
                if voxelSizeIn is None:
                    raise ValueError("No voxel recieved.","voxel_problem")
                else:
                    try:
                        self.intensities.Set(intensitiesIn)
                    except:
                        raise ValueError("Can not set array from the argument.","data_problem")
                    try:
                        self.voxel.Set(voxelSizeIn)
                    except:
                        raise ValueError("Can not set voxel from the argument.","voxel_problem")
        else:
            if intensitiesIn is None:
                intensitiesFile,tagString = self.LoadImageFile(fpath, 270)
                if tagString == "" :
                    if voxelSizeIn is None:
                        raise ValueError("No voxel recieved from file or as argument","voxel_problem")
                    else:
                        try:
                            self.intensities.Set(intensitiesFile)
                        except:
                            raise ValueError("Can not set array from file.","data_problem")
                        try:
                            self.voxel.Set(voxelSizeIn)
                        except:
                            raise ValueError("Can not set voxel from argument.","voxel_problem")
                else:
                    if voxelSizeIn is None:
                        try:
                            self.intensities.Set(intensitiesFile)
                        except:
                            raise ValueError("Can not set array from file.","data_problem")
                        try:
                            try:
                                voxelSizeIn = json.loads(tagString)
                            except :
                                raise ValueError("Can not convert tag. Check tag format.","voxel_problem")
                            self.voxel.Set( [voxelSizeIn["Z"], voxelSizeIn["X"], voxelSizeIn["Y"]] ) 
                        except:
                            raise ValueError("Can not set voxel from tag. Check tag format.","voxel_problem")
                    else:
                        try:
                            self.intensities.Set(intensitiesFile)
                        except:
                            raise ValueError("Can not set array from file.","data_problem")
                        try:
                            self.voxel.Set(voxelSizeIn)
                        except:
                            raise ValueError("Can not set voxel from argument.","voxel_problem")
            else:
                raise ValueError("Only one source of data for pixel values allowed","data_problem")

            self.path =  fpath[0] 
    # -------------------- constructor end ----------------------------

    # methods

    def LoadImageFile(self, fileNameList: tuple, tagID = 270)->tuple:
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

    def SetIntensities(self, newArray: np.ndarray):
        """
        Setting pixel array values
        """
        try:
            self.intensities.Set(newArray)
        except:
            raise ValueError("Can not set array from the argument.","data_problem")

    def GetIntensities(self)->np.ndarray:
        """
        Getting pixel array values
        """
        return self.intensities.Get()

    def SetVoxel(self, newVoxel: list):
        """
            Setting voxel with check
        """
        try:
            self.voxel.Set(newVoxel)
        except:
            raise ValueError("Can not set voxel from the argument.","voxel_problem")


    def GetVoxel(self)->list:
        """
            Getting list of voxel values
        """
        return self.voxel.Get()
    
    def SetVoxelToAxis(self, axisName:str, newValue:float):
        """
            Setting voxel value by axis name
        """
        try:
            self.voxel.SetToAxis(axisName, newValue)
        except:
            raise ValueError("Can not set voxel from the argument.","voxel_problem")
        
    def RescaleZ(self, newZVoxelSize):
        """
            Rescale over z. newZVoxelSize in micrometers
        """
        # теперь разбрасываем бид по отдельным массивам .
        oldShape = self.intensities.GetShape()

        zcoord = np.arange(oldShape[0]) * self.voxel.GetFromAxis("Z")
        xcoord = np.arange(oldShape[1]) * self.voxel.GetFromAxis("Y")
        ycoord = np.arange(oldShape[2]) * self.voxel.GetFromAxis("X")
        shapeZ = int(zcoord[oldShape[0] - 1] / newZVoxelSize)
        # print(
        #     "voxel size, oldshape, shapeZ :",
        #     self.voxelSize[0],
        #     oldShape[0],
        #     (shapeZ),
        # )
        zcoordR = np.arange(shapeZ) * newZVoxelSize
        interp_fun = RegularGridInterpolator((zcoord, xcoord, ycoord), self.intensities)

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
        self.intensities = beadInterp
        self.voxel.SetToAxis("Z", newZVoxelSize)

    
    def GetImageInfoStr(self, output:str = None):
        """
            Return options:
            "full" - full string info with array and voxel parameters.
            "json_voxel" - json string with voxel parameters.
            default - short info with resolution and voxel parameters.
        """
        match output:
            case "full":
                return "Image size(z,y,x)px: " + str(self.intensities.GetShape()) + "  Voxel(\u03BCm): " + str(self.voxel.Get())
            case "json_voxel":
                return json.dumps(self.voxel.GetDict())
            case _:
                return str( self.intensities.GetShape() ) + str(self.voxel.Get())


    def ShowClassInfo( self ):
        """
            Prints class attributes. 
        """
        print( " ImageClassInfo: " )
        print( " path: ", self.path )
        print( " voxel(micrometres): ", self.voxel.GetValuesStr() )
        print( " image shape: ", self.intensities.GetShape() )

    def SaveAsTiff(self, filename="img", outtype="uint8"):
        """
        Save Image as TIFF file
        Input: filename - path to file, including file name
               outtype - bit type for output
        """
        print("Trying to save TIFF file", outtype)
        try:
            tagID = 270
            strVoxel = json.dumps(self.voxel.GetDict())
            imlist = []
            for tmp in self.intensities:
                imlist.append(Image.fromarray(tmp.astype(outtype)))
            #imlist[0].tag[270] = strVoxel
            imlist[0].save(
                filename, tiffinfo={tagID:strVoxel}, save_all=True, append_images=imlist[1:]
            )
        except:
            raise IOError("Cannot save file "+filename,"file_not_saved")
        print("File saved in ", filename)

    # context manager support.........
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        return None



    #---------------------------------



if __name__ == "__main__":
    pass        
