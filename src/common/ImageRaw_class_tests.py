import unittest
import os
import numpy as np
from  ImageRaw_class import ImageRaw




class ImageRawClassTests(unittest.TestCase):
    """Test for implementation of ImageRaw class"""
    def setUp(self):
        self.testVoxel = [0.1,0.02,0.02]
        self.testArray = np.random.randint(0, 100, size=(5, 10, 10))
        

    def test_ConstructorFromFile(self):
        folderPath = os.getcwd()+'\\data\\image_array\\'
        self.filelist = []
        self.filelist = [folderPath+name for name in os.listdir(path = folderPath)]
        with ImageRaw(fpath = self.filelist, voxelSizeIn=self.testVoxel) as img:
            # white layer test
            self.testArray = np.zeros((36,36))
            np.testing.assert_array_equal(img.GetIntensities()[0,:,:], self.testArray, 'create from file 0 error')
            #black layer test
            self.testArray = np.ones((36,36)) * 255
            np.testing.assert_array_equal(img.GetIntensities()[1,:,:], self.testArray, 'create from file 255 error')
            #halfblack
            self.testArray[:,18:]=self.testArray[:,18:] * 0
            np.testing.assert_array_equal(img.GetIntensities()[3,:,:], self.testArray, 'create from file 255 error')



    def test_ConstructorFromArray(self):
        img = ImageRaw(voxelSizeIn=self.testVoxel, intensitiesIn = self.testArray)
        # using numpy.testing.assert_array_equal to avoid ambiguous ValueError
        np.testing.assert_array_equal(img.GetIntensities(),self.testArray,'create from array error')
        

    def test_ConstructorExceptionVoxel(self):
        with self.assertRaises(ValueError):
            img = ImageRaw(voxelSizeIn=[0,-1,-2], intensitiesIn = self.testArray)

    def test_ConstructorExceptionArray(self):
        with self.assertRaises(ValueError):
            img = ImageRaw(voxelSizeIn=[0,-1,-2], intensitiesIn = self.testArray)
        pass

    def test_LoadFileImage(self):
        # testVoxel = [0.1,0.02,0.05]
        # testExemplar = ImageRaw(fileList,testVoxel)
        self.filelist = []

        self.assertEqual(1, 1)
        pass

    def test_SetVoxel(self):
        img = ImageRaw(voxelSizeIn = [1, 2, 3], intensitiesIn = self.testArray)
        self.assertEqual( img.voxel.GetFromAxis("Z"), 1, 'wrong Z voxel' )
        self.assertEqual( img.voxel.GetFromAxis("Y"), 2, 'wrong Y voxel' )
        self.assertEqual( img.voxel.GetFromAxis("X"), 3, 'wrong X voxel' )
    
    def test_SetVoxelList(self):
        img = ImageRaw(voxelSizeIn = [1, 2, 3], intensitiesIn = self.testArray)
        img.SetVoxel([4, 5, 6])
        self.assertEqual( img.voxel.GetFromAxis("Z"), 4, 'wrong Z voxel' )
        self.assertEqual( img.voxel.GetFromAxis("Y"), 5, 'wrong Y voxel' )
        self.assertEqual( img.voxel.GetFromAxis("X"), 6, 'wrong X voxel' )

    def test_SetVoxelAtAxis(self):
        img = ImageRaw(voxelSizeIn = [1, 2, 3], intensitiesIn = self.testArray)
        img.SetVoxelToAxis("Z", 7)
        self.assertEqual( img.voxel.GetFromAxis("Z"), 7, 'wrong Z voxel' )
        img.SetVoxelToAxis("Y", 8)
        self.assertEqual( img.voxel.GetFromAxis("Y"), 8, 'wrong Y voxel' )
        img.SetVoxelToAxis("X", 9)
        self.assertEqual( img.voxel.GetFromAxis("X"), 9, 'wrong X voxel' )

    def test_SetArray(self):
        img = ImageRaw(voxelSizeIn=self.testVoxel, intensitiesIn = self.testArray)
        newArray = np.random.randint(0, 100, size=(5, 10, 10))
        img.intensities.Set(newArray)
        # using numpy.testing.assert_array_equal to avoid ambiguous ValueError
        np.testing.assert_array_equal(img.GetIntensities(),newArray,'create from array error')

    def test_GetImageInfoStr(self):
        img = ImageRaw(voxelSizeIn=self.testVoxel, intensitiesIn = self.testArray)
        tStr = "Image size(z,y,x)px: " + str(self.testArray.shape) + "  Voxel(\u03BCm): " + str(self.testVoxel)
        self.assertEqual( img.GetImageInfoStr(output = "full"), tStr, 'wrong full output' )
        tStr = str( self.testArray.shape ) + str(self.testVoxel)
        self.assertEqual( img.GetImageInfoStr(), tStr, 'wrong default output' )

        
def RunTests() -> None:
    print("===============================================\n",
          "Running tests for ImageRaw class.\n",
          "===============================================")
    unittest.main()

if __name__=="__main__":
    RunTests()
