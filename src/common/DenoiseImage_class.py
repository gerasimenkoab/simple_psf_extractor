# denoising
import numpy as np
from scipy.ndimage import median_filter, gaussian_filter
from scipy.signal import wiener
from skimage.restoration import denoise_tv_chambolle, denoise_nl_means, denoise_bilateral
import pywt
#from keras.models import load_model


class DenoiseImage:
    """
    Class for image denoising methods
    """

    def __init__(self, image: np.ndarray):
        """
        Constructor
        """
        self._image = image

    def bilateral(self, sigma_color: float, sigma_spatial: float)->np.ndarray:
        """
        Apply bilateral filter to denoise the image series
        """
        if self._image.shape[0] == 1:
            return denoise_bilateral(self._image, sigma_color=sigma_color, sigma_spatial=sigma_spatial)
        else:
            resultImage = np.zeros_like(self._image)
            for i in range(self._image.shape[0]):
                resultImage[i] = denoise_bilateral(self._image[i], sigma_color=0.05, sigma_spatial=15)
            return resultImage
    
    # def withNNModel(self, modelPath: str)->np.ndarray:
    #     """
    #     Use CNN model to denoise the image series
    #     UNet of DnCNN model can be used
    #     """
    #     # Load the trained DnCNN model
    #     model = load_model(modelPath)

    #     # Initialize an array to hold the denoised images
    #     denoisedImages = np.zeros_like(self._image)

    #     # Iterate over the first dimension of the array
    #     for i in range(self._image.shape[0]):
    #         # Normalize the image to the range [0, 1]
    #         imageNormalized = self._image[i].astype('float32') / 255.0
    #         # Add extra dimensions to the image for the batch size and channels
    #         imageNormalized = np.expand_dims(np.expand_dims(imageNormalized, axis=0), axis=-1)

    #         denoisedImage = model.predict(imageNormalized)
    #         # Remove the extra dimensions and scale back to the range [0, 255]
    #         denoisedImages[i] = np.squeeze(denoisedImage) * 255.0
    #     return denoisedImages


    def median(self, size: int)->np.ndarray:
        """
        Apply median filter to denoise the image series
        """
        resultImages = np.zeros_like(self._image)
        for i in range(self._image.shape[0]):
            resultImages[i] = median_filter(self._image[i], size=size)
        return resultImages

    def gaussian(self, sigma: float)->np.ndarray:
        """
        Apply Gaussian filter to denoise the image series
        """
        resultImages = np.zeros_like(self._image)
        for i in range(self._image.shape[0]):
            resultImages[i] = gaussian_filter(self._image[i], sigma=sigma)
        return resultImages

    def wiener(self, mysize=None)->np.ndarray:
        """
        Apply Wiener filter to denoise the image series
        """
        resultImages = np.zeros_like(self._image)
        for i in range(self._image.shape[0]):
            resultImages[i] = wiener(self._image[i], mysize=mysize)
        return resultImages

    def totalVariation(self, weight: float)->np.ndarray:
        """
        Apply Total Variation filter to denoise the image series
        """
        resultImages = np.zeros_like(self._image)
        for i in range(self._image.shape[0]):
            resultImages[i] = denoise_tv_chambolle(self._image[i], weight=weight)
        return resultImages

    def nonLocalMeans(self, patchSize: int, patchDistance: int)->np.ndarray:
        """
        Apply Non-Local Means filter to denoise the image series
        """
        resultImages = np.zeros_like(self._image)
        for i in range(self._image.shape[0]):
            resultImages[i] = denoise_nl_means(self._image[i], patch_size=patchSize, patch_distance=patchDistance)
        return resultImages

    def wavelet(self, mode='soft')->np.ndarray:
        """
        Apply Wavelet filter to denoise the image series
        """
        resultImages = np.zeros_like(self._image)
        for i in range(self._image.shape[0]):
            coeffs = pywt.wavedec2(self._image[i], 'db8')
            coeffs = pywt.threshold(coeffs, value=np.std(coeffs)/2, mode=mode)
            resultImages[i] = pywt.waverec2(coeffs, 'db8')
        return resultImages