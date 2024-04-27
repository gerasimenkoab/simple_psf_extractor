import numpy as np
import json


class Voxel:
    """
    Class for voxel:
        attributes:
        _voxelValues: List [z,y,x]
        _axisNames: Tuple ("Z", "Y", "X")
    """
    # Voxel axis names static variable
    _axisNames:tuple = ("Z", "Y", "X")

    def __init__(self, voxelSizeIn: list = None):
        super().__init__()
        self._voxelValues:list = None
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

    def SetFromDict(self, newVoxel: dict)->None:
        """
            Setting voxel from dict
        """
        if newVoxel is not None:
            try:
                self._voxelValues = [newVoxel[axisName] for axisName in self._axisNames]
            except KeyError:
                raise ValueError("Wrong Voxel Value.")

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
