import numpy as np
from PIL import Image, UnidentifiedImageError



class FileManipulation:
    """
    Class for tiff file manipulation methods.

    """
    def LoadMultiframeTiff(fileName:str = None)->tuple:
        """Load single multiframe tiff file and return numpy array with pixel values.
        Input: fileName - path to file
        Output (imgArray, imageTiff.tag) - tuple with numpy array with pixel values and tiff tags as dictionary
        Raises: IOError
        """

        try:
            if fileName is None or fileName == "" or not isinstance(fileName, str): 
                raise ValueError("File name is empty or None or more than one file name given")
            with Image.open(fileName) as imageTiff:
                ncols, nrows = imageTiff.size
                nlayers = imageTiff.n_frames
                imgArray = np.ndarray([nlayers, nrows, ncols]) # Z,Y,X
                if imageTiff.mode == "I" or imageTiff.mode == "L":
                    for i in range(nlayers):
                        imageTiff.seek(i)
                        imgArray[i, :, :] = np.array(imageTiff)
                elif imageTiff.mode == "RGB":
                    for i in range(nlayers):
                        imageTiff.seek(i)
                        imageTiff.getdata()
                        r, g, b = imageTiff.split()
                        ra = np.array(r)
                        ga = np.array(g)
                        ba = np.array(b)
                        #recalculate greyscale intensity from rgb values
                        grayImgArr = 0.299 * ra + 0.587 * ga + 0.114 * ba
                        imgArray[i, :, :] = grayImgArr
                else:
                    raise ValueError( "Unsupported tiff file mode: {}".format( str(imageTiff.mode) ) )          
        except (FileNotFoundError, UnidentifiedImageError, ValueError) as e:
            raise IOError("Can't load file: {} "+ str(e).format(fileName) )
        return imgArray, imageTiff.tag

    def LoadSingleFrameTiffArray( fileNameList:list = None)->tuple:
        """Load multiple singleframe tiff files and return numpy array with pixel values.
        Input: fileNameList - list of file names
        Output: imgArray, imageTiff.tag) - tuple with numpy array with pixel values and tiff tags as dictionary
        Raises: IOError
        """
        try:
            if fileNameList is None or len(fileNameList) < 2:
                raise ValueError("List of file is empty or has only one file")
            
            with Image.open(fileNameList[0]) as image_preread:
                nlayers = len(fileNameList)
                ncols, nrows = image_preread.size
                imgArray = np.ndarray([nlayers, nrows, ncols])
                
                if image_preread.mode == "RGB":
                    for i, fileName in enumerate(fileNameList):
                        try: 
                            with Image.open(fileName) as imageTiff:
                                if imageTiff.n_frames != 1:
                                    raise ValueError("File is not single frame: {}".format(fileName))
                                imageTiff.getdata()
                                r, g, b = imageTiff.split()
                                tagReturn = imageTiff.tag
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
                            with Image.open(fileName) as imageTiff:
                                imgArray[i, :, :] = np.array(imageTiff)
                                tagReturn = imageTiff.tag
                        except:
                            raise FileNotFoundError("Can't load file: {} ".format(fileName))
                else:
                    raise ValueError("Unsupported tiff file mode: {}".format(str(imageTiff.mode)))
        except (FileNotFoundError, UnidentifiedImageError, ValueError) as e:
            raise IOError("Can't load file: {} "+ str(e).format(fileNameList) )
        return imgArray, tagReturn

    def SaveAsTiff( imageArray: np.ndarray = None, fileName:str = "img", tagString:str = None, outType:str = "uint8"):
        """
        Save Image as TIFF file
        Input: fileName - path to file, including file name
                outType - bit type for output
                tagString - string to be saved in tiff file
        Output: None
        Raises: IOError
        """
        if imageArray is None or len(imageArray) == 0:
            raise IOError("Image array recieved is None or Empty. Cannot save file "+fileName,"file_not_saved")
        # fileName end with .tiff or .tif then do nothing else add .tif
        if not fileName.endswith(".tiff") and not fileName.endswith(".tif"):
            fileName = fileName + ".tif"
        try:
            tagID = 270
            imlist = []
            for tmp in imageArray:
                imlist.append(Image.fromarray(tmp.astype(outType)))
            imlist[0].save(
                fileName, tiffinfo={tagID:tagString}, save_all=True, append_images=imlist[1:]
            )
            return imlist
        except IOError as e:
            raise IOError("Error during file write. Cannot save file "+fileName,"file_not_saved")
