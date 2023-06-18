import numpy as np
from PIL import Image
from PIL.TiffTags import TAGS
from tkinter.filedialog import askopenfilenames
import traceback



def ReadTiffToArray(fileNameList: tuple, tagID = 270):
    """
    Function ReadTiffToArray() reads tiff stack from file name list
        Input:
            fileName - path to file
            tagID - tag index (default 270 - file info)
        Returns tuple : (imgArray , tag)
            imgArray : ndarray  - array of pixel values in grayscale
            tag : str - tag string for tagID
    """
    print("Loading Images from files. ", end=" ")
    
    if len(fileNameList) < 1:
        raise ValueError("Empty file name list")
    elif len(fileNameList) == 1:
        # single file load
        try:
            image_tiff = Image.open(fileNameList[0])
        except :
            raise FileNotFoundError("Can't load file: {} ".format(fileName) )
        print("Color_mode:", image_tiff.mode, ".......", end=" ")

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
                grayImgArr = 0.299 * ra + 0.587 * ga + 0.114 * ba
                imgArray[i, :, :] = grayImgArr
        else:
            raise ValueError( "Unsupported tiff file mode: {}".formatstr( str(image_tiff.mode) ) )          

    else:
        # multi file load
        try:
            image_preread = Image.open(fileNameList[0])
        except:
            raise Exception
        print("color_mode:", image_preread.mode, ".......", end=" ")
        nlayers = len(fileNameList)
        ncols, nrows = image_preread.size
        imgArray = np.ndarray([nlayers, nrows, ncols])
        # checking file color mode and convert to grayscale
        if image_preread.mode == "RGB":
            # convert to Grayscale
            for i, fileName in enumerate(fileNameList):
                try: 
                    image_tiff = Image.open(fileName)
                except :
                    raise FileNotFoundError( "Can't load file: {} ".format( fileName ) )
                if image_tiff.n_frames != 1:
                    raise ValueError( "Not singleframe tif file in list of files: {}".format( fileName ) )
                image_tiff.getdata()
                r, g, b = image_tiff.split()
                ra = np.array(r)
                ga = np.array(g)
                ba = np.array(b)
                grayImgArr = 0.299 * ra + 0.587 * ga + 0.114 * ba
                imgArray[i, :, :] = grayImgArr
        elif image_preread.mode == "I" or image_preread.mode == "L":
            for i, fileName in enumerate(fileNameList):
                imgArray[i, :, :] = np.array(Image.open(fileName))
        else:
            raise ValueError( "Unsupported tiff file mode: {}".formatstr( str(image_tiff.mode) ) )
    print("Done.")
    try:
        return imgArray, image_tiff.tag[tagID][0]
    except:
        return imgArray, ""

if __name__ == "__main__":
    # testing file loading
    fileList = askopenfilenames(title="Load Photo")
    try:
        arr = ReadTiffToArray(fileList)
        print(arr[0].shape,arr[1])
    except:
        traceback.print_exc()
    
