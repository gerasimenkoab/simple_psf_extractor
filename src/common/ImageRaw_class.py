import numpy as np
import logging
import itertools
import os
import glob
import xml.etree.ElementTree as ET
from scipy.interpolate import RegularGridInterpolator

import json
try: # for running as package
    from .Voxel_class import Voxel
    from .intensities_class import IntensityValues
    from .FileManipulation_class import FileManipulation
except: # for testing purposes
    from Voxel_class import Voxel
    from intensities_class import IntensityValues
    from FileManipulation_class import FileManipulation

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
        else: #if fpath is not None
            if intensitiesIn is None:
                try:
                    intensitiesFile,tagString = self.LoadImageFile(fpath, 270)
                    self._intensities.Set(intensitiesFile)
                except IOError:
                    raise ValueError("Can not load array from file.","data_problem")
                except ValueError:
                    raise ValueError("Can not set array from file.","data_problem")

                if voxelSizeIn is None:

                    if tagString == None:
                        try:
                            try:
                                parameters = self.LoadProjectSeriesParameters(fpath[0])
                                self._voxel.SetFromDict(parameters["voxel"])
                            except:
                                raise ValueError("No voxel recieved from file or as argument","voxel_problem")
                        except:
                            raise ValueError("Can not set voxel from file.","voxel_problem")
                    else:
                        try:
                            try:
                                voxelSizeDict = json.loads(tagString)
                            except TypeError:
                                raise ValueError("json.loads() was called with a non-string argument")
                            except json.JSONDecodeError:
                                raise ValueError("json.loads() was called with an invalid JSON string")
                            self._voxel.SetFromDict( voxelSizeDict ) 
                        except ValueError:
                            raise ValueError("Can not set voxel from tag. Check tag format.","voxel_problem")
                        
                else:
                    try:
                        self._voxel.Set(voxelSizeIn)
                    except:
                        raise ValueError("Can not set voxel from argument.","voxel_problem")
                    
            else: #if intensitiesIn is not None and fpath is not None
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
            try:
                imgArray, tagDict = FileManipulation.LoadMultiframeTiff(fileNameList[0])
            except IOError:
                raise 
        else:
            # multi file load
            try:
                imgArray,tagDict = FileManipulation.LoadSingleFrameTiffArray(fileNameList)
            except IOError:
                raise
        try:
            return imgArray, tagDict[tagID][0]
        except:
            return imgArray, None

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

    def SaveAsTiff(self, filename:str = "img", outtype:str = "uint8"):
        """
        Save Image as TIFF file
        Input: filename - path to file, including file name
               outtype - bit type for output
        """
        try:
            img_tiff = FileManipulation.SaveAsTiff(imageArray =  self._intensities.Get(),
                                        fileName = filename, 
                                        tagString = json.dumps(self._voxel.GetDict()),
                                        outType = outtype)
            return img_tiff
        except IOError as e:
            self.logger.error("Can't save file "+filename)
            raise IOError("File save failed: "+filename,"file_not_saved")
        self.logger.info("File saved at "+filename)

    # context manager support.........
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        return None



    #---------------------------------



if __name__ == "__main__":
    pass        
