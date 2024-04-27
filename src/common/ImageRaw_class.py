import numpy as np
import logging
import itertools
import os
import glob
import xml.etree.ElementTree as ET
from scipy.interpolate import RegularGridInterpolator
from PIL import Image
import json
try: # for running as package
    from common.Voxel_class import Voxel
    from common.Intensities_class import IntensityValues
except: # for testing purposes
    from Voxel_class import Voxel
    from Intensities_class import IntensityValues

class ImageRaw:
    """
    Class for image:
        attributes:
        self._intensities: IntensityValues - array of pixel intensities
        self._voxel: Voxel - voxel sizes in each dimension
        self.path: str - path to file
    """


    def __init__(
        self, fpath : str = None, voxelSizeIn : list = None, intensitiesIn : np.ndarray = None
    )->None:
        super().__init__()
        self.logger = logging.getLogger("__main__." + __name__)
        self._intensities = IntensityValues()
        self._voxel = Voxel() 
        self.path = ""
        if fpath is None:
            if intensitiesIn is None:
                raise ValueError("No data recieved.","data_problem")
            else:
                if voxelSizeIn is None:
                    raise ValueError("No voxel recieved.","voxel_problem")
                else:
                    try:
                        self._intensities.Set(intensitiesIn)
                    except:
                        raise ValueError("Can not set array from the argument.","data_problem")
                    try:
                        self._voxel.Set(voxelSizeIn)
                    except:
                        raise ValueError("Can not set voxel from the argument.","voxel_problem")
        else:
            if intensitiesIn is None:
                intensitiesFile,tagString = self.LoadImageFile(fpath, 270)
                try:
                    self._intensities.Set(intensitiesFile)
                except:
                    raise ValueError("Can not set array from file.","data_problem")

                if tagString == "" :
                    if voxelSizeIn is None:
                        try:
                            parameters = self.LoadProjectSeriesParameters(fpath[0])
                            self._voxel.SetFromDict(parameters["voxel"])
                        except:
                            raise ValueError("No voxel recieved from file or as argument","voxel_problem")
                    else:
                        try:
                            self._voxel.Set(voxelSizeIn)
                        except:
                            raise ValueError("Can not set voxel from argument.","voxel_problem")
                else:
                    if voxelSizeIn is None:
                        try:
                            try:
                                voxelSizeIn = json.loads(tagString)
                            except :
                                raise ValueError("Can not convert tag. Check tag format.","voxel_problem")
                            self._voxel.Set( [voxelSizeIn["Z"], voxelSizeIn["X"], voxelSizeIn["Y"]] ) 
                        except:
                            raise ValueError("Can not set voxel from tag. Check tag format.","voxel_problem")
                    else:
                        try:
                            self._voxel.Set(voxelSizeIn)
                        except:
                            raise ValueError("Can not set voxel from argument.","voxel_problem")
            else:
                raise ValueError("Only one source of data for pixel values allowed","data_problem")

            self.path =  fpath[0] 
    # -------------------- constructor end ----------------------------



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
            imgArray = self.LoadMultiframeTiff(fileNameList[0])
        else:
            # multi file load
            try:
                imgArray = self.LoadSingleFrameTiffArray(fileNameList)
            except:
                raise FileNotFoundError("Can't load file: {} ".format(fileNameList[0]) )
        try:
            return imgArray, image_tiff.tag[tagID][0]
        except:
            return imgArray, ""

    def LoadProjectSeriesParameters(self, currentFilePath: str):
        # load parameters from xml file stored in MetaData subfolder of current folder
        #  in file with a file name ended with"Propertires.xml"
        # return dictionary with parameters
        
        metadataPath = os.path.dirname(currentFilePath)+"\\MetaData"
        # Find the "Properties.xml" file in the metadata directory
        propertiesFile = glob.glob(os.path.join(metadataPath, "*Properties.xml"))
        if propertiesFile:
            properties_file = propertiesFile[0]
        else:
            raise FileNotFoundError("No 'Properties.xml' file found in the metadata directory")

        # Parse the XML file
        tree = ET.parse(properties_file)
        root = tree.getroot()
        parameters = {}
        voxel = {}
        # Iterate over all elements in the XML file
        for element in root.iter():
            if element.tag == "DimensionDescription" :
                voxel[element.attrib['DimID']] = float(element.attrib['Voxel'])
                parameters['voxel'] = voxel
            if element.tag == "ATLConfocalSettingDefinition":
                for attr in element.attrib:
                    if attr in ["Zoom", "NumericalAperture", "RefractionIndex",
                                "Pinhole", "PinholeAiry", "EmissionWavelengthForPinholeAiryCalculation"]:
                        try:
                            parameters[attr] = float(element.attrib[attr])
                        except:
                            parameters[attr] = element.attrib[attr] 
        return parameters


    def LoadMultiframeTiff(self,fileName)->np.ndarray:
        """Load single multiframe tiff file and return numpy array with pixel values."""

        try:
            with Image.open(fileName) as image_tiff:
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
            raise FileNotFoundError("Can't load file: {} ".format(fileName) )
        return imgArray

    def LoadSingleFrameTiffArray(self, fileNameList)->np.ndarray:
        """Load multiple singleframe tiff files and return numpy array with pixel values."""

        with Image.open(fileNameList[0]) as image_preread:
            nlayers = len(fileNameList)
            ncols, nrows = image_preread.size
            imgArray = np.ndarray([nlayers, nrows, ncols])
            
            if image_preread.mode == "RGB":
                for i, fileName in enumerate(fileNameList):
                    try: 
                        with Image.open(fileName) as image_tiff:
                            if image_tiff.n_frames != 1:
                                raise ValueError("Not singleframe tif file in list of files: {}".format(fileName))
                            image_tiff.getdata()
                            r, g, b = image_tiff.split()
                    except:
                        raise FileNotFoundError("Can't load file: {} ".format(fileName))
                    
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
                        raise FileNotFoundError("Can't load file: {} ".format(fileName))
            else:
                raise ValueError("Unsupported tiff file mode: {}".format(str(image_tiff.mode)))
        return imgArray




    def SetIntensities(self, newArray: np.ndarray)->None:
        """
        Setting pixel array values
        """
        try:
            self._intensities.Set(newArray)
        except:
            raise ValueError("Can not set array from the argument.","data_problem")

    def SetVoxel(self, newVoxel: list):
        """
            Setting voxel with check
        """
        try:
            self._voxel.Set(newVoxel)
        except:
            raise ValueError("Can not set voxel from the argument.","voxel_problem")

 
    def SetVoxelToAxis(self, axisName:str, newValue:float):
        """
            Setting voxel value by axis name
        """
        try:
            self._voxel.SetToAxis(axisName, newValue)
        except:
            raise ValueError("Can not set voxel from the argument.","voxel_problem")
        
    def GetIntensities(self)->np.ndarray:
        """
        Getting pixel array values
        """
        return self._intensities.Get()
    
    def GetIntensitiesLayer(self, layer:int)->np.ndarray:
        """
        Getting pixel array values for layer
        """
        return self._intensities.GetLayer(layer)

    def GetVoxel(self)->list:
        """
            Getting list of voxel values
        """
        return self._voxel.Get()
    
    def GetVoxelDict(self)->dict:
        """
            Getting voxel values as dict
        """
        return self._voxel.GetDict()

    def GetVoxelFromAxis(self, axisName:str)->float:
        """
            Getting voxel value by axis name
        """
        return self._voxel.GetFromAxis(axisName)
    
    def GetImageShape(self)->tuple:
        """
            Getting image shape
        """
        return self._intensities.GetShape()
        
    def RescaleZ(self, newZVoxelSize)->None:
        """
            Rescale over z. newZVoxelSize in micrometers
        """
        oldShape = self._intensities.GetShape()

        zcoord = np.arange(oldShape[0]) * self._voxel.GetFromAxis("Z")
        xcoord = np.arange(oldShape[1]) * self._voxel.GetFromAxis("Y")
        ycoord = np.arange(oldShape[2]) * self._voxel.GetFromAxis("X")
        shapeZ = int(zcoord[oldShape[0] - 1] / newZVoxelSize)
        zcoordR = np.arange(shapeZ) * newZVoxelSize
        interp_fun = RegularGridInterpolator((zcoord, xcoord, ycoord), self._intensities)

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
        self._intensities = beadInterp
        self._voxel.SetToAxis("Z", newZVoxelSize)

    
    def GetImageInfoStr(self, output:str = None)->str:
        """
            Return options:
            "full" - full string info with array and voxel parameters.
            "json_voxel" - json string with voxel parameters.
            default - short info with resolution and voxel parameters.
        """
        match output:
            case "full":
                return "Image size(z,y,x)px: " + str(self._intensities.GetShape()) + "  Voxel(\u03BCm): " + str(self._voxel.Get())
            case "json_voxel":
                return json.dumps(self._voxel.GetDict())
            case _:
                return str( self._intensities.GetShape() ) + str(self._voxel.Get())


    def ShowClassInfo( self ):
        """
            Prints class attributes. 
        """
        print(" ")
        print( " ImageClassInfo: " )
        print( " path: ", self.path )
        print( " voxel(micrometres): ", self._voxel.GetValuesStr() )
        print( " image shape: ", self._intensities.GetShape() )

    def SaveAsTiff(self, filename:str = "img", outtype:str = "uint8")->None:
        """
        Save Image as TIFF file
        Input: filename - path to file, including file name
               outtype - bit type for output
        """
        # filename end with .tiff or .tif then do nothing else add .tif
        if not filename.endswith(".tiff") and not filename.endswith(".tif"):
            filename = filename + ".tif"
        self.logger.info("Trying to save TIFF file. Type: "+outtype)
        try:
            tagID = 270
            strVoxel = json.dumps(self._voxel.GetDict())
            imlist = []
            for tmp in self._intensities:
                imlist.append(Image.fromarray(tmp.astype(outtype)))
            #imlist[0].tag[270] = strVoxel
            imlist[0].save(
                filename, tiffinfo={tagID:strVoxel}, save_all=True, append_images=imlist[1:]
            )
        except:
            self.logger.error("Can't save file "+filename)
            raise IOError("Cannot save file "+filename,"file_not_saved")
        self.logger.info("File saved at "+filename)

    # context manager support.........
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        return None



    #---------------------------------



if __name__ == "__main__":
    pass        
