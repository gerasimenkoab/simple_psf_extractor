# denoising
import numpy as np
from scipy.ndimage import median_filter, gaussian_filter
from scipy.signal import wiener
from skimage.restoration import denoise_tv_chambolle, denoise_nl_means, denoise_bilateral
import pywt
#from keras.models import load_model





class ImageDenoiser:
    """Interface  class for denoising"""
    def __init__(self, methodName:str = None):
        if methodName is not None:
            self._method = Gaussian()
        else:
            self.setMethod(methodName)
    
    def denoise(self, image:np.ndarray)->np.ndarray:
        return self._method.run(image)

    def setMethod(self, methodName:str, **kwargs):
        if methodName == 'Gaussian':
            sigma = kwargs.get('sigma', 1)  # replace default_value with a default sigma value
            self._method = Gaussian(sigma)
        elif methodName == 'Median':
            size = kwargs.get('size', 3)  # replace default_value with a default size value
            self._method = Median(size)
        else:
            raise ValueError("Method not implemented")
        
class Nothing:
    """Do nothing with image"""
    def run(image:np.ndarray) -> np.ndarray:
        return image

class Gaussian:
    def __init__(self, sigma:float = None):
        if not isinstance(sigma, float):
            raise ValueError("Sigma should be float")
        if sigma is None:
            self._sigma = 1
        else:
            self._sigma = sigma
    
    def run(image:np.ndarray, sigma: float)->np.ndarray:
        """
        Apply Gaussian filter to denoise the image series
        """
        resultImages = np.zeros_like(image)
        for i in range(image.shape[0]):
            resultImages[i] = gaussian_filter(image[i], sigma=self._sigma)
        return resultImages

class Median:
    def __init__(self, size:int = None) -> None:
        if size is None:
            self._size = 3

    def run(image:np.ndarray, size: int)->np.ndarray:
        """
        Apply median filter to denoise the image series
        """
        resultImages = np.zeros_like(image)
        for i in range(image.shape[0]):
            resultImages[i] = median_filter(image[i], size=size)
        return resultImages
    




class DenoiseImage:
    """
    Class for image denoising methods
    """
    _implementedMethodList = ['none', 'Gaussian', 'Wiener', 'Total Variation', 'Median', 'Non-Local Means', 'Bilateral', 'Wavelet']

    @staticmethod
    def getImplementedMethodsList()->list:
        """
        Get the list of implemented denoising methods
        """
        return DenoiseImage._implementedMethodList
    
    @staticmethod
    def none(image:np.ndarray)->np.ndarray:
        """
        No denoising applied
        """
        return image
    
    def denoiseByMethodParam( image:np.ndarray, method:str, **kwargs)->np.ndarray:
        """
        Apply the denoising method by name
        """
        match method:
            case 'none':
                return DenoiseImage.none(image)
            case 'Bilateral':
                return DenoiseImage.bilateral(image, **kwargs)
            case 'Median':
                return DenoiseImage.median(image, **kwargs)
            case 'Gaussian':
                return DenoiseImage.gaussian(image, **kwargs)
            case 'Wiener':
                return DenoiseImage.wiener(image, **kwargs)
            case 'Total Variation':
                return DenoiseImage.totalVariation(image, **kwargs)
            case 'Non-Local Means':
                return DenoiseImage.nonLocalMeans(image, **kwargs)
            case 'Wavelet':
                return DenoiseImage.wavelet(image, **kwargs)
            case _:
                raise ValueError("Method not implemented")

    def denoiseByMethodDefault( image:np.ndarray, method:str)->np.ndarray:
        """
        Apply the denoising method by name with default parameters
        """
        match method:
            case 'none':
                return DenoiseImage.none(image)
            case 'Bilateral':
                return DenoiseImage.bilateral(image, sigma_color=0.05, sigma_spatial=15)
            case 'Median':
                return DenoiseImage.median(image, size=3)
            case 'Gaussian':
                return DenoiseImage.gaussian(image, sigma=1)
            case 'Wiener':
                return DenoiseImage.wiener(image, mysize=None)
            case 'Total Variation':
                return DenoiseImage.totalVariation(image, weight=0.1)
            case 'Non-Local Means':
                return DenoiseImage.nonLocalMeans(image, patchSize=7, patchDistance=11)
            case 'Wavelet':
                return DenoiseImage.wavelet(image, mode='soft')
            case _:
                raise ValueError("Method not implemented")

    @staticmethod
    def bilateral(image:np.ndarray, sigma_color: float, sigma_spatial: float)->np.ndarray:
        """
        Apply bilateral filter to denoise the image series
        """
        if image.shape[0] == 1:
            return denoise_bilateral(image, sigma_color=sigma_color, sigma_spatial=sigma_spatial)
        else:
            resultImage = np.zeros_like(image)
            for i in range(image.shape[0]):
                resultImage[i] = denoise_bilateral(image[i], sigma_color=0.05, sigma_spatial=15)
            return resultImage
    
    # def withNNModel(_image:np.ndarray, modelPath: str)->np.ndarray:
    #     """
    #     Use CNN model to denoise the image series
    #     UNet of DnCNN model can be used
    #     """
    #     # Load the trained DnCNN model
    #     model = load_model(modelPath)

    #     # Initialize an array to hold the denoised images
    #     denoisedImages = np.zeros_like(_image)

    #     # Iterate over the first dimension of the array
    #     for i in range(_image.shape[0]):
    #         # Normalize the image to the range [0, 1]
    #         imageNormalized = _image[i].astype('float32') / 255.0
    #         # Add extra dimensions to the image for the batch size and channels
    #         imageNormalized = np.expand_dims(np.expand_dims(imageNormalized, axis=0), axis=-1)

    #         denoisedImage = model.predict(imageNormalized)
    #         # Remove the extra dimensions and scale back to the range [0, 255]
    #         denoisedImages[i] = np.squeeze(denoisedImage) * 255.0
    #     return denoisedImages

    @staticmethod
    def median(image:np.ndarray, size: int)->np.ndarray:
        """
        Apply median filter to denoise the image series
        """
        resultImages = np.zeros_like(image)
        for i in range(image.shape[0]):
            resultImages[i] = median_filter(image[i], size=size)
        return resultImages

    @staticmethod
    def gaussian(image:np.ndarray, sigma: float)->np.ndarray:
        """
        Apply Gaussian filter to denoise the image series
        """
        resultImages = np.zeros_like(image)
        for i in range(image.shape[0]):
            resultImages[i] = gaussian_filter(image[i], sigma=sigma)
        return resultImages

    @staticmethod
    def wiener(image:np.ndarray, mysize=None)->np.ndarray:
        """
        Apply Wiener filter to denoise the image series
        """
        resultImages = np.zeros_like(image)
        for i in range(image.shape[0]):
            resultImages[i] = wiener(image[i], mysize=mysize)
        return resultImages

    @staticmethod
    def totalVariation(image:np.ndarray, weight: float)->np.ndarray:
        """
        Apply Total Variation filter to denoise the image series
        """
        resultImages = np.zeros_like(image)
        for i in range(image.shape[0]):
            resultImages[i] = denoise_tv_chambolle(image[i], weight=weight)
        return resultImages

    @staticmethod
    def nonLocalMeans(image:np.ndarray, patchSize: int = 7, patchDistance: int = 11)->np.ndarray:
        """
        Apply Non-Local Means filter to denoise the image series
        Other possible default values:
        patch_size=7,     # 7x7 patches
        patch_distance=11, # maximum distance between patches to be considered as similar
        h=0.1,             # cut-off distance (higher values mean more smoothing)
        multichannel=True, # set to True if the image is color
        fast_mode=True     # if True, a faster, but less accurate version of the algorithm is used
 
        """
        resultImages = np.zeros_like(image)
        for i in range(image.shape[0]):
            resultImages[i] = denoise_nl_means(image[i], patch_size=patchSize, patch_distance=patchDistance)
        return resultImages

    @staticmethod
    def wavelet(image:np.ndarray, mode='soft')->np.ndarray:
        """
        Apply Wavelet filter to denoise the image series
        """
        resultImages = np.zeros_like(image)
        for i in range(image.shape[0]):
            array2D = image[i,:,:].reshape((image.shape[1],image.shape[2]))
            coeffs = pywt.wavedec2(array2D, 'db8')
            coeffs[0] = pywt.threshold(coeffs[0], value=np.std(coeffs[0])/2, mode=mode)
            for j in range(1, len(coeffs)):
                coeffs[j] = tuple(pywt.threshold(detail_coeff, value=np.std(detail_coeff)/2, mode=mode) for detail_coeff in coeffs[j])
            resultImages[i] = pywt.waverec2(coeffs, 'db8')
        return resultImages