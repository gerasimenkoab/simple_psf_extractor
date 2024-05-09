import numpy as np
from math import sqrt
from scipy import signal 
from scipy.special import jv
from scipy.ndimage import laplace
from itertools import product, repeat
from multiprocessing import Pool, Manager
from os import cpu_count, getpid

import time

class DeconMethods:
    """Class provides methods for deconvolution of PSF and images.
        Multithread version of deconvolution is used for image deconvolution.
    """
    def __init__(self):
        pass

    @staticmethod
    def DeconPSF(
        image: np.ndarray = None, 
        beadSizePx: int = None,
        zoomFactor: float = 2.6,
        beadVoxel: dict = None,
        iterNum: int = 1,
        deconType: str = "RL", 
        lambdaR: float = 0.000001, 
        progBar = None,
        parentWin = None
    ):
        """
        General function for restoration of PSF. Singlethreaded since image size is small.
        Input:
            image: np.ndarray  - averaged single bead image
            beadSizePx: int - actual bead size in pixels
            zoomFactor: float - zoom of bead circle  from microscope
            beadVoxel: dict - voxel sizes in dict in micrometer
            iterNum: int - number of iteration steps
            deconType: str  - deconvolution method name ( default - RL)
            lambdaR: float - regularization coefficient
            progBar : ttk.progressbar - progressbar to update
            parentWin : tkinter window widget
        Returns:
            imagePSF: np.ndarray
        """
        imagePSF: np.ndarray

        idealSphereArray =  DeconMethods.MakeIdealSphereArray(image.shape[0], beadSizePx, zoomFactor,
                                        beadVoxel["X"], beadDiameter = 0.2)
        match deconType:
            case "RL":
                # Richardson Lucy
                print(deconType," selected")
                            
                imagePSF = DeconMethods.MaxLikelhoodEstimationFFT_3D(
                    image,
                    idealSphereArray,
                    iterNum, False, progBar, parentWin
                )
            case "RLTMR":
                # Richardson Lucy with Tikhonov-Miller regularisation
                imagePSF = DeconMethods.DeconvolutionRLTMR(
                    image,
                    idealSphereArray,
                    lambdaR,
                    iterNum, False, progBar, parentWin
                )
            case "RLTVR":
                # Richardson Lucy with Total Variation regularisation
                imagePSF = DeconMethods.DeconvolutionRLTVR(
                    image,
                    idealSphereArray,
                    lambdaR,
                    iterNum, False, progBar, parentWin
                )
            case _:
                imagePSF = None
                print("DeconPSF: Invalid option. Please choose a valid option.")


        return imagePSF

    @staticmethod
    def _checkQueue(q, progBar, parentWin):
        """Auxilary function to check queue and update progressbar"""
        while progBar['value'] < progBar.cget("maximum"):
            progress = q.get() * DeconMethods.pb_step
            progBar['value'] += progress
            # print("Progress: ", progBar['value'])
            parentWin.update_idletasks()

        
 
    @staticmethod
    def DeconImage(
        image: np.ndarray, 
        kernell: np.ndarray,
        iterNum: int, 
        deconType: str, 
        lambdaR: float, 
        progBar = None, 
        parentWin = None
    ):
        """
        General function for restoration of image with known PSF(kernell) with multiprocessing usage
        Input:
            image: np.ndarray  - averaged single bead image
            kernell: np.ndarray - PSF or other kernell
            iterNum: int - number of iteration steps
            deconType: str  - deconvolution method name ( default - RL)
            lambdaR: float - regularization coefficient
            progBar : ttk.progressbar - progressbar to update
            parentWin : tkinter window widget( for progressbar update)

        Returns:
            imagePSF: np.ndarray
        """
        imageDeconvolved = np.copy(image)
        poolSize = cpu_count() - 2
        # chunkNumber = int(sqrt(poolSize))
        chunkNumber = int((poolSize))
        chunkDimX = image.shape[2] // chunkNumber # chunk size X
        chunkDimY = image.shape[1] // chunkNumber # chunk size Y
        chunkList = [] 
        # crating list of image chunks
        for i in range(0, image.shape[1], chunkDimY):
            if i <= image.shape[1]-chunkDimY:
                iEnd = i + chunkDimY
            else:
                iEnd= i + image.shape[1] % chunkDimY
            for j in range(0,image.shape[2], chunkDimX):
                if j <= image.shape[2]-chunkDimX:
                    jEnd = j + chunkDimX
                else:
                    jEnd= j + image.shape[2] % chunkDimX
                chunkList.append(image[:,i:iEnd, j:jEnd])

        DeconMethods.totalChunks = len(chunkList)
        DeconMethods.pb_step = progBar.cget("maximum") / DeconMethods.totalChunks
        progBar['value'] = 0
        parentWin.update_idletasks()
        # Don't use  tkinter progressbar with Pool() since tkinter is not thread safe and elements cant be
        # shared between threads. Use Manager() and Queue() to get values from threads and update progressbar.
        with Manager() as manager:
            q = manager.Queue()
            with Pool(processes = poolSize) as workers:
                if deconType == "RL":
                    # Richardson Lucy
                    argsList = zip(chunkList,
                                repeat(kernell),
                                repeat(iterNum),
                                repeat(False),
                                repeat(q)
                                )
                    # chunkListDec = workers.starmap(DeconMethods.MaxLikelhoodEstimationFFT_3D, argsList)
                    asyncResult = workers.starmap_async(DeconMethods.MaxLikelhoodEstimationFFT_3D, argsList)
                    DeconMethods._checkQueue(q, progBar, parentWin)
                    chunkListDec = asyncResult.get() 
                elif deconType == "RLTMR":
                    # Richardson Lucy with Tikhonov-Miller regularisation
                    argsList = zip(chunkList,
                        repeat(kernell),
                        repeat(lambdaR),
                        repeat(iterNum),
                        repeat(False),
                        repeat(q)
                        ) 
                    asyncResult = workers.starmap_async(DeconMethods.DeconvolutionRLTMR, argsList)
                    DeconMethods._checkQueue(q, progBar, parentWin)
                    chunkListDec = asyncResult.get() 
                elif deconType == "RLTVR":
                    # Richardson Lucy with Total Variation regularisation
                    argsList = zip(chunkList,
                        repeat(kernell),
                        repeat(lambdaR),
                        repeat(iterNum),
                        repeat(False),
                        repeat(q)
                        ) 
                    asyncResult = workers.starmap_async(DeconMethods.DeconvolutionRLTVR, argsList)
                    DeconMethods._checkQueue(q, progBar, parentWin)
                    chunkListDec = asyncResult.get() 
                else:
                    chunkListDec = None
                    print("DeconImage: Invalid option. Please choose a valid option.")

        # collect chunks into array.
        chunkID = 0
        for i in range(0, image.shape[1], chunkDimY):
            if i <= image.shape[1]-chunkDimY:
                iEnd = i + chunkDimY
            else:
                iEnd= i + image.shape[1] % chunkDimY
            for j in range(0,image.shape[2], chunkDimX):
                if j <= image.shape[2]-chunkDimX:
                    jEnd = j + chunkDimX
                else:
                    jEnd= j + image.shape[2] % chunkDimX
                imageDeconvolved[:,i:iEnd, j:jEnd] = chunkListDec[chunkID] 
                chunkID += 1
        return imageDeconvolved

    @staticmethod
    def PointFunction(pt, r0, r, maxIntensity):
        """
        Function of sphere of radius r with center in r0.
        Function return maxIntensity if pt in sphere and 0 if out of sphere.
        pt and r0 are np.array vectors : np.array([x,y,z])
        """
        if (pt - r0).dot(pt - r0) <= r * r:
            result = maxIntensity
        else:
            result = 0
        return result


    @staticmethod
    def PointFunctionAiry(pt, r0, maxIntensity=255, zoomfactor=2.6, beadVoxelSize = 0.044, beadDiameter = 0.2):
        """
        Zoom of bead circle  from microscope
        Radius = self.BeadDiameter / 2
        Center  r0 - np.array[0:2].
        Function return Airy disk intesity within first circle if pt in sphere and 0 if out of sphere.
        pt and r0 are np.array vectors : np.array([x,y,z])
        All  dimension in pixels are equal to x-dimension
        """

        l = abs(r0[0] - pt[0]) * beadVoxelSize
        r = beadDiameter / 2.0
        if r**2 - l**2 > 0:
            R = np.sqrt(r**2 - l**2) * zoomfactor
            ptd = pt * beadVoxelSize
            r0d = r0 * beadVoxelSize

            distSq = (ptd[1] - r0d[1]) ** 2 + (ptd[2] - r0d[2]) ** 2
            dist = np.sqrt(distSq)
            x = dist / R * 4.0
            if abs(x) >= 0.00001:  # Zero-criterion
            #     # NOTE: If 'x' is equal zero - result == nan!. To prevent it - make result equal 'maxIntensity'
                result = (2.0 * jv(1, x) / x) ** 2 * maxIntensity
            else:
                result = maxIntensity

        else:
            result = 0

        return result

    @staticmethod    
    def MakeIdealSphereArray(imgSize=36, sphRadius=5, zoomfactor=2.6,
                beadVoxelSize = 0.044, beadDiameter = 0.2):
        """
        Create ideal  sphere array corresponding to sphere_type
        Following parameters can be found in microscope project xml file:
        zoomFactor - zoom of bead circle  from microscope
        beadVoxelSize - voxel size in microns
        beadDiameter - bead diameter in microns
        """
        imgMidCoord = int(imgSize / 2)
        # imgSize = self.sideHalf *2
        imgCenter = np.array([imgMidCoord, imgMidCoord, imgMidCoord])
        tiffDraw = np.ndarray([imgSize, imgSize, imgSize])
        print("image size:", imgSize)
        print("sphere radius:", sphRadius)

        # tiffBit = self.tiffMenuBitDict[self.tiffSaveBitType.get()]

        # NOTE: get max intensity for different output bits types
        # lightIntensity = np.iinfo(tiffBit).max
        lightIntensity = 255

        for i, j, k in product(range(imgSize), repeat=3):
            tiffDraw[i, j, k] = DeconMethods.PointFunctionAiry(
                np.array([i, j, k]), imgCenter, 
                lightIntensity, zoomfactor=zoomfactor,
                beadVoxelSize = beadVoxelSize, beadDiameter = beadDiameter
            )
        print("Sphere created")
        return tiffDraw

    @staticmethod
    def LoadIdealSphereArray(imgSize=36, sphRadius=5):
        """create ideall sphere array"""
        imgMidCoord = 0.5 * (imgSize)
        imgCenter = np.array([imgMidCoord, imgMidCoord, imgMidCoord])
        tiffDraw = np.ndarray([imgSize, imgSize, imgSize])
        lightIntensity = 1000
        for i in range(imgSize):
            for j in range(imgSize):
                for k in range(imgSize):
                    tiffDraw[i, j, k] = DeconMethods.PointFunction(
                        np.array([i, j, k]), imgCenter, sphRadius, lightIntensity
                    )
        return tiffDraw

    @staticmethod
    def MaxLikelhoodEstimationFFT_3D(image, kernell, iterLimit=20, debug_flag=False,  q=None):
        """
        Function for  convolution with (Maximum likelihood estimaton)Richardson-Lucy method
        For psf calculation kernell = ideal sphere
        """
        f_0 = image
        # if there is NAN in image array(seems from source image) replace it with zeros
        f_0[np.isnan(f_0)] = 1.e-11
        f_0[f_0<1.e-11] = 1.e-11
        beadMaxInt = np.amax(image)
        padSize = kernell.shape
        f_0 = np.pad(f_0, list(zip(padSize, padSize)), "edge")
        b_noize = (np.mean(f_0[0, 0, :]) + np.mean(f_0[0, :, 0]) + np.mean(f_0[:, 0, 0])) / 3

        if debug_flag:
            print("Chunk on process: %d" %getpid())
            print("Debug output:")
            print(np.mean(f_0[0, 0, :]), np.mean(f_0[0, :, 0]), np.mean(f_0[:, 0, 0]))
            print(np.amax(f_0[0, 0, :]), np.amax(f_0[0, :, 0]), np.amax(f_0[:, 0, 0]))
            print(f_0[0, 0, 56], f_0[0, 56, 0], f_0[56, 0, 0])
        # preparing for start of iteration cycle
        f_i = f_0
        # starting iteration cycle
        for i in range(0, iterLimit):
            try:
                # first convolution
                e = signal.fftconvolve(f_i, kernell, mode="same")
                e = e + b_noize
                r = f_0 / e
                # possible zero check 
                # print(getpid(),np.any(e == 0))
                # with np.errstate(all='raise'):
                #     try:
                #         print(getpid(),"zero:",e.size - np.count_nonzero(e))
                #         r = f_0 / e # this gets caught and handled as an exception
                #     except FloatingPointError:
                #         print(getpid(),'oh no!')
                # second convolution
                pReversed = np.flip(kernell)
                rConv = signal.fftconvolve(r, pReversed, mode="same")
                rConv = np.real(rConv)
                rConv = rConv.clip(min=0)
                f_i = f_i * rConv

                f_i = f_i / np.amax(f_i) * beadMaxInt
            except:
                print("Deconvolution failed on iteration number: %d" %i)
                raise ValueError("Deconvolution failed")

        # end of iteration cycle
        if q!= None:
            q.put(1)
        return f_i[padSize[0]:-padSize[0], padSize[1]:-padSize[1], padSize[2]:-padSize[2]]

    @staticmethod
    def DeconvolutionRLTMR(
        image: np.ndarray,
        psf: np.ndarray,
        lambdaTM: float = 0.0001,
        iterLimit: int = 20,
        debug_flag=False,
        q = None
    ):
        """
        Function for  convolution Richardson Lucy Tikhonov Miller Regularization

        Parameters:
            image (ndarray): The 3D image to be deconvolved.
            psf (ndarray): The point spread function (PSF) of the imaging system.
            lambdaTM (float): The weight of the tikhonov miller regularization term. Defaults to 0.0001.
            iterLimit (int): The number of iterations to perform. Defaults to 10.
            debug_flag (bool) : debug output
            pb : tkinter.ttk.progressbar progressbar widget
            parentWin : tkinter window widget instance
    
        Returns:
            ndarray: The deconvolved image.    
        """

        f_0 = image
        # if there is NAN in image array(seems from source image) replace it with zeros
        f_0[np.isnan(f_0)] = 1.e-11
        f_0[f_0<1.e-11] = 1.e-11
        padSize = psf.shape
        b_noize = (np.mean(f_0[0, 0, :]) + np.mean(f_0[0, :, 0]) + np.mean(f_0[:, 0, 0])) / 3
        f_0 = np.pad(f_0, list(zip(padSize, padSize)), "edge")
        beadMaxInt = np.amax(image)
        p = psf

        if debug_flag:
            print("Debug output:")
            print("Background intensity:", b_noize, "Max intensity:", np.amax(f_0))
            print(
                "Deconvoluiton input shape (image, padded, psf):",
                image.shape,
                f_0.shape,
                psf.shape,
            )
        # preparing for start of iteration cycle
        f_old = f_0
        # starting iteration cycle
        # totaltime = time.time()
        for i in range(0, iterLimit):
            # first convolution
            starttime = time.time()
            e = signal.fftconvolve(f_old, p, mode="same")
            e = e + b_noize
            r = f_0 / e
            # second convolution
            p1 = np.flip(p)
            rnew = signal.fftconvolve(r, p1, mode="same")
            rnew = np.real(rnew)
            regTM = 1.0 + 2.0 * lambdaTM * laplace(f_old)
            f_old = f_old * rnew / regTM
            f_old = f_old / np.amax(f_old) * beadMaxInt

        if q!= None:
            q.put(1)
        f_old = f_old[padSize[0]:-padSize[0], padSize[1]:-padSize[1], padSize[2]:-padSize[2]]

        if debug_flag:
            print("Debug output:")
            print("Input image shape: ", image.shape)
            print("Deconvoluiton output shape :", f_old.shape)

        return f_old


    @staticmethod
    def DeconvolutionRLTVR(
        image: np.ndarray,
        psf: np.ndarray,
        lambdaTV=0.0001,
        iterLimit=10,
        debug_flag=False,
        q = None
    ):
        """
        Perform Richardson-Lucy deconvolution on a 3D image using a given point spread function (psf)
        with total variation regularization.

        Parameters:
            image (ndarray): The 3D image to be deconvolved.
            psf (ndarray): The point spread function (PSF) of the imaging system.
            lambdaTV (float): The weight of the total variation regularization term. Defaults to 0.0001.
            iterLimit (int): The number of iterations to perform. Defaults to 10.
            debug_flag (bool) : debug output
            pb : tkinter.ttk.progressbar progressbar widget
            parentWin : tkinter window widget instance
    
        Returns:
            ndarray: The deconvolved image.    
        """

        f_0 = image
        # if there is NAN in image array(seems from source image) replace it with zeros
        f_0[np.isnan(f_0)] = 1.e-11
        f_0[f_0<1.e-11] = 1.e-11
        padSize = psf.shape
        f_0 = np.pad(f_0, list(zip(padSize, padSize)), "edge")
        beadMaxInt = np.amax(image)
        p = psf
        b_noize = (np.mean(f_0[0, 0, :]) + np.mean(f_0[0, :, 0]) + np.mean(f_0[:, 0, 0])) / 3

        if debug_flag:
            print("Debug output:")
            print("Background intensity:", b_noize, "Max intensity:", np.amax(f_0))
            print(
                "Deconvoluiton input shape (image, padded, psf):",
                image.shape,
                f_0.shape,
                psf.shape,
            )
        #    b_noize = 0.1
        # preparing for start of iteration cycle
        f_old = f_0
        # starting iteration cycle
        lambdaTV = 0.005
        for k in range(0, iterLimit):
            # first convolution
            e = signal.fftconvolve(f_old, p, mode="same")
            e = e + b_noize
            r = f_0 / e
            # second convolution
            p1 = np.flip(p)
            rnew = signal.fftconvolve(r, p1, mode="same")
            rnew = np.real(rnew)
            #      rnew = rnew.clip(min=0)
            # https://stackoverflow.com/questions/11435809/compute-divergence-of-vector-field-using-python
            # regTV = 1.0 - lambdaTV * divergence(np.gradient(f_old))
            gr = np.gradient(f_old)
            regTV = 1.0 - lambdaTV * np.sqrt(gr[0] ** 2 + gr[1] ** 2 + gr[2] ** 2)
            f_old = f_old * rnew / regTV
            f_old = f_old / np.amax(f_old) * beadMaxInt
        if q!= None:
            q.put(1)
        # end of iteration cycle
        f_old = f_old[padSize[0]:-padSize[0], padSize[1]:-padSize[1], padSize[2]:-padSize[2]]

    
        if debug_flag:
            print("Debug output:")
            print("Input image shape: ", image.shape)
            print("Deconvoluiton output shape :", f_old.shape)

        return f_old

    #   ================= obsolete code =================================
    # def DeconImageOld(
    #     image: np.ndarray, kernell: np.ndarray,
    #     iterNum: int, deconType: str, lambdaR: float, progBar, parentWin
    # ):
    #     """    
    #     General function for restoration of image with known PSF(kernell). Single threaded.
    #     Input:
    #         image: np.ndarray  - averaged single bead image
    #         kernell: np.ndarray - PSF or other kernell
    #         iterNum: int - number of iteration steps
    #         deconType: str  - deconvolution method name ( default - RL)
    #         lambdaR: float - regularization coefficient
    #         progBar : ttk.progressbar - progressbar to update
    #         parentWin : tkinter window widget

    #     Returns:
    #         imagePSF: np.ndarray
    #     """
    #     chunkID=0
    #     imageDeconvolved = np.copy(image)
    #     chunkDimX = image.shape[2] // 4 # chunk size X
    #     chunkDimY = image.shape[1] // 4 # chunk size Y
    #     for i in range(0, image.shape[1], chunkDimY):
    #         if i <= image.shape[1]-chunkDimY:
    #             iEnd = i + chunkDimY
    #         else:
    #             iEnd= i + image.shape[1] % chunkDimY
    #         for j in range(0,image.shape[2], chunkDimX):
    #             if j <= image.shape[1]-chunkDimY:
    #                 jEnd = j + chunkDimX
    #             else:
    #                 jEnd= j + image.shape[2] % chunkDimX
    #             imageChunk = image[:,i:iEnd, j:jEnd]
    #             print("Chunk number %03d" %(chunkID))
    #             chunkID += 1
    #             if deconType == "RL":
    #                 # Richardson Lucy
    #                 chunkDeconvolved = MaxLikelhoodEstimationFFT_3D(
    #                     imageChunk, kernell,
    #                     iterNum, False, progBar, parentWin
    #                 )
    #             elif deconType == "RLTMR":
    #                 # Richardson Lucy with Tikhonov-Miller regularisation
    #                 chunkDeconvolved = DeconvolutionRLTMR(
    #                     imageChunk, kernell,
    #                     lambdaR, iterNum, False, progBar, parentWin
    #                 )
    #             elif deconType == "RLTVR":
    #                 # Richardson Lucy with Total Variation regularisation
    #                 chunkDeconvolved = DeconvolutionRLTVR(
    #                     imageChunk, kernell,
    #                     lambdaR, iterNum, False, progBar, parentWin
    #                 )
    #             else:
    #                 imageDeconvolved = None
    #                 print("DeconImage: Invalid option. Please choose a valid option.")

    #             imageDeconvolved[:,i:iEnd, j:jEnd] = chunkDeconvolved 
    #     return imageDeconvolved

    # def DeconvolutionRL(image, psf, iterLimit=20, debug_flag=False):
    #     """Function for  convolution"""

    #     f_0 = image
    #     # if there is NAN in image array(seems from source image) replace it with zeros
    #     f_0[np.isnan(f_0)] = 0.0
    #     # do image padding
    #     pad = psf.shape
    #     f_0 = np.pad(f_0, ((pad[0], pad[0]), (pad[1], pad[1]), (pad[2], pad[2])), "edge")
    #     beadMaxInt = np.amax(image)

    #     p = psf

    #     b_noize = (np.mean(f_0[0, 0, :]) + np.mean(f_0[0, :, 0]) + np.mean(f_0[:, 0, 0])) / 3

    #     if debug_flag:
    #         print("Debug output:")
    #         print("Background intensity:", b_noize, "Max intensity:", np.amax(f_0))
    #         print(
    #             "Deconvoluiton input shape (image, padded, psf):",
    #             image.shape,
    #             f_0.shape,
    #             psf.shape,
    #         )
    #     # preparing for start of iteration cycle
    #     f_old = f_0
    #     # starting iteration cycle
    #     for k in range(0, iterLimit):
    #         print("\r", "iter:", k, end=" ")
    #         # first convolution
    #         e = signal.fftconvolve(f_old, p, mode="same")
    #         # e = np.real(e)
    #         e = e + b_noize
    #         r = f_0 / e
    #         # second convolution
    #         p1 = np.flip(p)
    #         rnew = signal.fftconvolve(r, p1, mode="same")
    #         rnew = np.real(rnew)
    #         #      rnew = rnew.clip(min=0)
    #         f_old = f_old * rnew
    #         f_old = f_old  # / np.amax(f_old) * beadMaxInt
    #     # end of iteration cycle
    #     imSh = f_0.shape
    #     pad = psf.shape
    #     f_old = f_old[
    #         pad[0] : imSh[0] - pad[0], pad[1] : imSh[1] - pad[1], pad[2] : imSh[2] - pad[2]
    #     ]
    #     if debug_flag:
    #         print("Debug output:")
    #         print("Deconvoluiton output shape :", f_old.shape)

    #     return f_old
