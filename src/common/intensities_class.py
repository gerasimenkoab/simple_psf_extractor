import numpy as np
from scipy.interpolate import RegularGridInterpolator



class IntensityValues:
    """
    Class for intensity values:
        attributes:
        self._pointIntensities: np.ndarray - array of pixel intensities
    """


    def __init__(self, pointIntensitiesIn: np.ndarray = None):
        super().__init__()
        self._pointIntensities: np.ndarray = None
        if pointIntensitiesIn is not None:
            self.Set(pointIntensitiesIn)

    def __iter__(self):
        """Iterator for layers in array"""
        for layer in self._pointIntensities:
            yield layer

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
