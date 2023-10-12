import unittest
import numpy as np
from  ImageRaw_class import ImageRaw


# for __main__ testing call
from tkinter import *
from tkinter.filedialog import askopenfilenames
import traceback


class ImageRawClassTests(unittest.TestCase):
    """Test for implementation of ImageRaw class"""
    def setUp(self):
        self.testVoxel = [0.1,0.02,0.02]
        self.testArray = np.random.randint(0, 100, size=(5, 10, 10))

    def test_ConstructorFromFile(self):
        self.filelist = []
        self.assertEqual(1,1)
        pass

    def test_ConstructorFromArray(self):
        img = ImageRaw(voxelSizeIn=self.testVoxel, imArrayIn = self.testArray)
        # using numpy.testing.assert_array_equal to avoid ambiguous ValueError
        np.testing.assert_array_equal(img.imArray,self.testArray,'create from array error')
        

    def test_ConstructorExceptionVoxel(self):
        with self.assertRaises(ValueError):
            img = ImageRaw(voxelSizeIn=[0,-1,-2], imArrayIn = self.testArray)

    def test_ConstructorExceptionArray(self):
        with self.assertRaises(ValueError):
            img = ImageRaw(voxelSizeIn=[0,-1,-2], imArrayIn = self.testArray)
        pass

    def test_LoadFileImage(self):
        # testVoxel = [0.1,0.02,0.05]
        # testExemplar = ImageRaw(fileList,testVoxel)
        self.filelist = []

        self.assertEqual(1, 1)
        pass

    def test_SetVoxel(self):
        img = ImageRaw(voxelSizeIn = [1, 2, 3], imArrayIn = self.testArray)
        self.assertEqual( img.voxel['Z'], 1, 'wrong Z voxel' )
        self.assertEqual( img.voxel['Y'], 2, 'wrong Y voxel' )
        self.assertEqual( img.voxel['X'], 3, 'wrong X voxel' )
 
    def test_SetArray(self):
        img = ImageRaw(voxelSizeIn=self.testVoxel, imArrayIn = self.testArray)
        newArray = np.random.randint(0, 100, size=(5, 10, 10))
        img.SetArray(newArray)
        # using numpy.testing.assert_array_equal to avoid ambiguous ValueError
        np.testing.assert_array_equal(img.imArray,newArray,'create from array error')

    def test_GetImageInfoStr(self):
        pass

        
def RunTests() -> None:
    print("===============================================\n",
          "Running tests for ImageRaw class.\n",
          "===============================================")
    unittest.main()

if __name__=="__main__":
    RunTests()

    fileList = askopenfilenames(title="Load Photo")
    try:
        testExemplar = ImageRaw(fileList)
    except ValueError as vE:
        traceback.print_exc()
        if vE.args[1] == "voxel_problem":
            testVoxel = [0.1,0.02,0.05]
            testExemplar = ImageRaw(fileList,testVoxel)
        else:
            print("Not voxel problem")
            quit()
