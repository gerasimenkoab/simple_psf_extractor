import numpy as np
from scipy.ndimage import median_filter, gaussian_filter
from scipy.signal import wiener
from skimage.restoration import denoise_tv_chambolle, denoise_nl_means, denoise_bilateral
import pywt

from denoiser.n2n.controller import DenoiseController, DenoiseMethods, MODEL_FOLDER_PATH
from denoiser.utils.data_loader import find_latest_model


# from keras.models import load_model


class ImageDenoiser:
    """Interface class for denoiser

    The class provides a method to denoise an image array
        implemented Methods = ['none',
                              'Gaussian',
                              'Wiener',
                              'Total Variation',
                              'Median',
                              'Non-Local Means',
                              'Bilateral',
                              'Wavelet']

    To add new method add class inheriting from DenoiseMethod and decorate it with @registerDenoiseMethodSubclass
    """
    _implementedMethodsDict = {}

    def setDenoiseMethod(self, methodName, **kwargs):
        if methodName in self._implementedMethodsDict:
            self._method = self._implementedMethodsDict[methodName](**kwargs)
        else:
            raise ValueError("Method not known")

    @staticmethod
    def getDnoiseMethodsList() -> list:
        """
        Get the list of implemented denoiser methods
        """
        return list(ImageDenoiser._implementedMethodsDict.keys())

    def denoise(self, imageArray: np.ndarray) -> np.ndarray:
        """ Apply the denoiser method to the image array
        Input:
            imageArray: np.ndarray  Image array to be denoised
        Output:
            np.ndarray: Denoised image array
        """
        try:
            return self._method.run(imageArray)
        except:
            raise RuntimeError("Denoising failed")


def registerDenoiseMethodSubclass(cls):
    """Decorator to register DenoiseMethod subclasses at runtime"""
    if not issubclass(cls, DenoiseMethod):
        raise ValueError("Class should be subclass of DenoiseMethod")
    if cls._methodName not in ImageDenoiser.getDnoiseMethodsList():
        ImageDenoiser._implementedMethodsDict[cls._methodName] = cls
    return cls


class DenoiseMethod:
    """Interface class for denoiser methods"""
    # def __init__(self, methodName:str):
    #     self._methodName = methodName
    _methodName = None

    def run(self, image: np.ndarray) -> np.ndarray:
        raise NotImplementedError("Method not implemented")

    def setParameters(self, **kwargs):
        raise NotImplementedError("Method not implemented")


@registerDenoiseMethodSubclass
class Nothing(DenoiseMethod):
    """Do nothing with image"""
    _methodName = "none"

    def run(self, image: np.ndarray) -> np.ndarray:
        return image


@registerDenoiseMethodSubclass
class Gaussian(DenoiseMethod):
    _methodName = "Gaussian"

    def __init__(self, sigma: float = None):
        if sigma is None:
            self._sigma = 1
        else:
            if not isinstance(sigma, float):
                raise ValueError("Sigma should be float")
            self._sigma = sigma

    def run(self, image: np.ndarray) -> np.ndarray:
        """
        Apply Gaussian filter to denoise the image series
        """
        resultImages = np.zeros_like(image)
        for i in range(image.shape[0]):
            resultImages[i] = gaussian_filter(image[i], sigma=self._sigma)
        return resultImages

    def setParameters(self, sigma: float):
        self._sigma = sigma


@registerDenoiseMethodSubclass
class Median(DenoiseMethod):
    _methodName = "Median"

    def __init__(self, size: int = None) -> None:
        if size is None:
            self._size = 3
        else:
            self._size = size

    def run(self, image: np.ndarray) -> np.ndarray:
        """
        Apply median filter to denoise the image series
        """
        resultImages = np.zeros_like(image)
        for i in range(image.shape[0]):
            resultImages[i] = median_filter(image[i], size=self._size)
        return resultImages

    def setParameters(self, size: int):
        self._size = size


@registerDenoiseMethodSubclass
class Wiener(DenoiseMethod):
    _methodName = "Wiener"

    def __init__(self, size=None) -> None:
        if size is None:
            self._size = 3
        else:
            self._size = size

    def run(self, image: np.ndarray) -> np.ndarray:
        """
        Apply Wiener filter to denoise the image series
        """
        resultImages = np.zeros_like(image)
        for i in range(image.shape[0]):
            resultImages[i] = wiener(image[i], mysize=self._size)
        return resultImages

    def setParameters(self, size: int):
        self._size = size


@registerDenoiseMethodSubclass
class TotalVariation(DenoiseMethod):
    _methodName = "Total Variation"

    def __init__(self, weight: float = None) -> None:
        if weight is None:
            self._weight = 0.1
        else:
            self._weight = weight

    def run(self, image: np.ndarray) -> np.ndarray:
        """
        Apply Total Variation filter to denoise the image series
        """
        resultImages = np.zeros_like(image)
        for i in range(image.shape[0]):
            resultImages[i] = denoise_tv_chambolle(image[i], weight=self._weight)
        return resultImages

    def setParameters(self, weight: float):
        self._weight = weight


@registerDenoiseMethodSubclass
class NonLocalMeans(DenoiseMethod):
    _methodName = "Non-Local Means"

    def __init__(self, patchSize: int = None, patchDistance: int = None) -> None:
        if patchSize is None:
            self._patchSize = 7
        else:
            self._patchSize = patchSize
        if patchDistance is None:
            self._patchDistance = 11
        else:
            self._patchDistance = patchDistance

    def run(self, image: np.ndarray) -> np.ndarray:
        """
        Apply Non-Local Means filter to denoise the image series
        """
        resultImages = np.zeros_like(image)
        for i in range(image.shape[0]):
            resultImages[i] = denoise_nl_means(image[i], patch_size=self._patchSize, patch_distance=self._patchDistance)
        return resultImages

    def setParameters(self, patchSize: int, patchDistance: int):
        self._patchSize = patchSize
        self._patchDistance = patchDistance


@registerDenoiseMethodSubclass
class Bilateral(DenoiseMethod):
    _methodName = "Bilateral"

    def __init__(self, sigma_color: float = None, sigma_spatial: float = None) -> None:
        if sigma_color is None:
            self._sigma_color = 0.05
        else:
            self._sigma_color = sigma_color
        if sigma_spatial is None:
            self._sigma_spatial = 15
        else:
            self._sigma_spatial = sigma_spatial

    def run(self, image: np.ndarray) -> np.ndarray:
        """
        Apply bilateral filter to denoise the image series
        """
        resultImages = np.zeros_like(image)
        for i in range(image.shape[0]):
            resultImages[i] = denoise_bilateral(image[i], sigma_color=self._sigma_color,
                                                sigma_spatial=self._sigma_spatial)
        return resultImages

    def setParameters(self, sigma_color: float, sigma_spatial: float):
        self._sigma_color = sigma_color
        self._sigma_spatial = sigma_spatial


@registerDenoiseMethodSubclass
class Wavelet(DenoiseMethod):
    _methodName = "Wavelet"

    def __init__(self, mode: str = None) -> None:
        if mode is None:
            self._mode = 'soft'
        else:
            self._mode = mode

    def run(self, image: np.ndarray) -> np.ndarray:
        """
        Apply Wavelet filter to denoise the image series
        """
        resultImages = np.zeros_like(image)
        for i in range(image.shape[0]):
            array2D = image[i, :, :].reshape((image.shape[1], image.shape[2]))
            coeffs = pywt.wavedec2(array2D, 'db8')
            coeffs[0] = pywt.threshold(coeffs[0], value=np.std(coeffs[0]) / 2, mode=self._mode)
            for j in range(1, len(coeffs)):
                coeffs[j] = tuple(
                    pywt.threshold(detail_coeff, value=np.std(detail_coeff) / 2, mode=self._mode) for detail_coeff in
                    coeffs[j])
            resultImages[i] = pywt.waverec2(coeffs, 'db8')
        return resultImages

    def setParameters(self, mode: str):
        self._mode = mode


@registerDenoiseMethodSubclass
class TriDeFusion(DenoiseMethod):
    _methodName = "TriDeFusion"

    def __init__(self, mode: DenoiseMethods = DenoiseMethods.N2N) -> None:
        self._mode = mode

    def run(self, image: np.ndarray) -> np.ndarray:
        controller = DenoiseController()
        if self._mode != 'NLM':
            _model_path, _creation_date, _model_version = find_latest_model(_folder_path=MODEL_FOLDER_PATH)
            controller.build_n2n_model(_model_path=_model_path, _model_version=_model_version)
        controller.preprocess_image(_source_img=image)
        controller.denoise(_type_method=self._mode)
        return controller.get_result()


if __name__ == "__main__":
    print("DenoiseImage_class.py: Running as main")
    print("DenoiseImage_class.py: Testing denoiser methods")
    # Create a test image
    image = np.random.rand(10, 100, 100) * 255
    image = image.astype(np.uint8)
    # Create a denoiser object
    denoiser = ImageDenoiser()
    print(f"Implemented denoiser methods: {denoiser.getDnoiseMethodsList()}")
    # Test the denoiser methods
    for method in denoiser.getDnoiseMethodsList():
        print(f"Testing method: {method}")
        denoiser.setDenoiseMethod(method)
        denoisedImage = denoiser.denoise(image)
        print(f"Shape of denoised image: {denoisedImage.shape}")
