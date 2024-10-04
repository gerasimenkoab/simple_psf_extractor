from enum import Enum
from math import floor
from typing import List

import cv2
import numpy as np
import torch
from PIL import Image
from matplotlib import cm
from torchvision import transforms

from denoiser.n2n.unet import UnetN2N, UnetN2Nv2, DIV
from denoiser.utils.data_loader import find_latest_model
from denoiser.utils.image_utils import normalize_image, load_image, save_image, gauss_blur, median_filter_img
from denoiser.utils.plot import ImageInfo, plot_image_slices, plot_lines_profile

#MODEL_FOLDER_PATH = './denoiser/experiments/pretrained/n2n/checkpoints'
MODEL_FOLDER_PATH = './denoiser/experiments/n2n/Apr_08'
NOISY_IMAGE_PATH = './denoiser/validation/test_strings.tif'
X_SCALE, Y_SCALE, Z_SCALE = 0.022, 0.022, 0.1


class DenoiseMethods(Enum):
    NLM = 'NLM'
    N2N = 'N2N'
    FIRST_NLM = 'NLM->N2N'
    FIRST_N2N = 'N2N->NLM'


class DenoiseController:
    def __init__(self):
        self.__model = None
        self.__clean_img = None  # for the synthetic images in validation
        self.__noisy_img = None
        self.__nlm_denoised_img = None
        self.__n2n_denoised_img = None
        self.__nlm_denoised_layers = []
        self.__n2n_denoised_layers = []
        self.__type_method = None

    def model_name(self) -> str:
        """
       Get the name of the neural network model.
       Returns:
           str: The name of the model.
       """
        return self.__model.__class__.__name__

    @property
    def clean_img(self):
        return self.__clean_img

    @property
    def noisy_img(self):
        return self.__noisy_img

    @noisy_img.setter
    def noisy_img(self, value):
        self.__noisy_img = value

    @property
    def nlm_denoised_img(self):
        return self.__nlm_denoised_img

    @property
    def n2n_denoised_img(self):
        return self.__n2n_denoised_img

    def build_n2n_model(self, _model_path: str, _model_version: int = 2, _device: str = 'cpu'):
        """
        Build a Noise2Noise model for denoiser.
        Args:
            _model_path (str): Path to the pre-trained model file.
            _model_version (int): Version of the model to use (default is 2).
            _device (str): Device to load the model on (default is 'cpu').
        """
        try:
            if _model_path is None:
                raise ValueError("Model path cannot be None")
            if _model_version is None:
                raise ValueError("Model version cannot be None")
            if _model_version not in [1, 2]:
                raise ValueError(f"Invalid model version: {_model_version}. Expected 1 or 2.")
            if _device is None:
                _device = 'cpu'

            self.__model = UnetN2Nv2(in_channels=1, out_channels=1) if _model_version == 2 else UnetN2N(in_channels=1,
                                                                                                        out_channels=1)
            self.__model.load_state_dict(torch.load(_model_path, map_location=torch.device(_device)))
            self.__model.eval()
            print("Model preloaded successfully!")
        except (ValueError, Exception) as e:
            print(f"Error in build_n2n_model: {str(e)}")
            raise

    @staticmethod
    def __prepare_layer(_layer: np.ndarray) -> np.ndarray:
        try:
            if _layer is None:
                raise ValueError("Pil Frame should be uint8 and cannot be None.")
            width = floor(_layer.shape[0] // DIV) * DIV
            height = floor(_layer.shape[1] // DIV) * DIV
            return _layer[:width, :height, ...]
        except (ValueError, Exception) as e:
            print(f"Error in prepare_frame: {str(e)}")
            raise

    @staticmethod
    def __postprocess_image(_x: np.ndarray) -> np.ndarray:
        try:
            if _x is None:
                raise ValueError("Pil Frame should be uint8 and cannot be None.")
            # _x = median_filter_img(_img=_x, _block_size=5)
            # _x = gauss_blur(_img=_x, gaussian_sigma=1)
            # _x /= 1.4
            #processed_img = normalize_image(_img=_x, dtype=_x.dtype)
            return _x.astype(np.uint8)
        except (ValueError, Exception) as e:
            print(f"Error in __n2n_postprocess_image: {str(e)}")
            raise

    def preprocess_image(self, _source_img: np.ndarray, _is_clean: bool = False) -> None:
        layer_list = []
        for layer in _source_img:
            if len(layer.shape) == 3:
                layer = cv2.cvtColor(layer, cv2.COLOR_BGR2GRAY)
            prepared_layer = self.__prepare_layer(_layer=layer)
            layer_list.append(Image.fromarray(prepared_layer.astype("uint8")))
        preprocessed_img = np.asarray([np.array(image) for image in layer_list], dtype=float)
        if _is_clean:
            self.__clean_img = normalize_image(_img=preprocessed_img, dtype=preprocessed_img.dtype)
        else:
            self.__noisy_img = normalize_image(_img=preprocessed_img, dtype=preprocessed_img.dtype)

    @staticmethod
    def __nlm_denoise_layer(_noisy_layer: np.ndarray) -> np.ndarray:
        try:
            if _noisy_layer is None:
                raise ValueError("Noisy layer cannot be None.")
            _noisy_layer = cv2.convertScaleAbs(_noisy_layer)
            _denoised_layer = cv2.fastNlMeansDenoising(_noisy_layer, None, 10, 7, 21)
            return _denoised_layer
        except (ValueError, Exception) as e:
            print(f"Error in nlm_denoise_layer: {str(e)}")
            raise

    def __n2n_denoise_layer(self, _noisy_layer: np.ndarray, _noisy_min: float, _noisy_max: float) -> np.ndarray:
        """
        Denoise a single layer from a noisy image using a Noise2Noise network.
        """
        try:
            if _noisy_layer is None:
                raise ValueError("Noisy layer cannot be None.")
            _noisy_tensor = self.__n2n_preprocess_image(_noisy_layer.astype(np.float32), _noisy_min,
                                                        _noisy_max).unsqueeze(0)
            with torch.no_grad():
                denoised_tensor = self.__model(_noisy_tensor)
            _denoised_layer = np.array(transforms.ToPILImage()(denoised_tensor.squeeze(0).cpu()))
            return _denoised_layer
        except (ValueError, Exception) as e:
            print(f"Error in n2n_denoise_layer: {str(e)}")
            raise

    @staticmethod
    def __n2n_preprocess_image(_x: np.ndarray, minval: float, maxval: float):
        preprocess = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5]),
            transforms.Lambda(lambda x: (x - minval) / (maxval - minval))
        ])
        return preprocess(_x)

    def n2n_denoise_image(self, _noisy_img: np.ndarray) -> None:
        try:
            for layer in _noisy_img:
                _denoised_layer = self.__n2n_denoise_layer(_noisy_layer=layer, _noisy_min=_noisy_img.min(),
                                                           _noisy_max=_noisy_img.max())
                if _denoised_layer is not None:
                    self.__n2n_denoised_layers.append(_denoised_layer)
            if len(self.__n2n_denoised_layers) != 0:
                n2n_denoised_img = np.array(self.__n2n_denoised_layers, dtype=float)
                self.__n2n_denoised_img = n2n_denoised_img
        except (ValueError, Exception) as e:
            print(f"Error in n2n_denoise_image: {str(e)}")
            raise

    def nlm_denoise_image(self, _noisy_img: np.ndarray) -> None:
        try:
            for layer in _noisy_img:
                _denoised_layer = self.__nlm_denoise_layer(_noisy_layer=layer)
                if _denoised_layer is not None:
                    self.__nlm_denoised_layers.append(_denoised_layer)
            if len(self.__nlm_denoised_layers) != 0:
                nlm_denoised_img = np.array(self.__nlm_denoised_layers, dtype=float)
                self.__nlm_denoised_img = nlm_denoised_img
        except (ValueError, Exception) as e:
            print(f"Error in nlm_denoise_image: {str(e)}")
            raise

    def denoise(self, _type_method: DenoiseMethods = DenoiseMethods.FIRST_NLM) -> None:
        try:
            assert self.__noisy_img is not None, (f"Noisy image is missing. Please provide a noisy image.\nFirst, do "
                                                  f"the preprocessing (preprocess_image). If necessary (for synthetic "
                                                  f"data) set the value for noisy image")
            if _type_method is None:
                raise ValueError("Type of denoiser method cannot be None.")
            self.__type_method = _type_method
            self.__nlm_denoised_layers = []
            self.__n2n_denoised_layers = []
            if self.__type_method == DenoiseMethods.NLM:
                self.nlm_denoise_image(_noisy_img=self.__noisy_img)
                self.__postprocess_image(_x=self.__nlm_denoised_img)
            elif self.__type_method == DenoiseMethods.N2N:
                self.n2n_denoise_image(_noisy_img=self.__noisy_img)
                self.__postprocess_image(_x=self.__n2n_denoised_img)
            elif self.__type_method == DenoiseMethods.FIRST_NLM:
                self.nlm_denoise_image(_noisy_img=self.__noisy_img)
                self.n2n_denoise_image(_noisy_img=self.__nlm_denoised_img)
                self.__postprocess_image(_x=self.__n2n_denoised_img)
            elif self.__type_method == DenoiseMethods.FIRST_N2N:
                self.n2n_denoise_image(_noisy_img=self.__noisy_img)
                self.nlm_denoise_image(_noisy_img=self.__n2n_denoised_img)
                self.__postprocess_image(_x=self.__nlm_denoised_img)
        except (ValueError, Exception) as e:
            print(f"Error in denoise: {str(e)}")
            raise

    def get_result(self) -> np.ndarray:
        try:
            if self.__type_method == DenoiseMethods.NLM or self.__type_method == DenoiseMethods.FIRST_N2N:
                return self.nlm_denoised_img
            elif self.__type_method == DenoiseMethods.N2N or self.__type_method == DenoiseMethods.FIRST_NLM:
                return self.n2n_denoised_img
        except (ValueError, Exception) as e:
            print(f"Error in get_result: {str(e)}")
            raise

    def get_info_images(self) -> List[ImageInfo]:
        try:
            assert self.__noisy_img is not None, (f"Noisy image is missing. Please provide a noisy image.\nFirst, do "
                                                  f"the preprocessing (preprocess_image). If necessary (for synthetic "
                                                  f"data) set the value for noisy image")
            if self.__type_method is None:
                raise ValueError("Type of denoiser method cannot be None. Run first the denoise function.")
            images = [(self.__noisy_img, 'Noisy image')]

            if self.__type_method == DenoiseMethods.NLM:
                if self.__nlm_denoised_img is None:
                    raise ValueError("NLM denoised image cannot be None. Run first the denoise function.")
                images.append((self.__nlm_denoised_img, 'NLM denoised image'))
            elif self.__type_method == DenoiseMethods.N2N:
                if self.__n2n_denoised_img is None:
                    raise ValueError("N2N denoised image cannot be None. Run first the denoise function.")
                images.append((self.__n2n_denoised_img, 'N2N denoised image'))
            elif self.__type_method == DenoiseMethods.FIRST_NLM:
                if self.__nlm_denoised_img is None or self.__n2n_denoised_img is None:
                    raise ValueError("NLM and N2N denoised image cannot be None. Run first the denoise function.")
                images.extend([(self.__nlm_denoised_img, 'NLM denoised image'), (self.__n2n_denoised_img,
                                                                                 'N2N denoised image')])
            elif self.__type_method == DenoiseMethods.FIRST_N2N:
                if self.__nlm_denoised_img is None or self.__n2n_denoised_img is None:
                    raise ValueError("NLM and N2N denoised image cannot be None. Run first the denoise function.")
                images.extend([(self.__n2n_denoised_img, 'N2N denoised image'), (self.__nlm_denoised_img,
                                                                                 'NLM denoised image')])
            if self.__clean_img is not None:
                images.insert(0, (self.__clean_img, 'Ground Truth image'))
            return images
        except (ValueError, Exception) as e:
            print(f"Error in get_info_images: {str(e)}")
            raise


if __name__ == "__main__":
    _model_path, _creation_date, _model_version = find_latest_model(_folder_path=MODEL_FOLDER_PATH)
    controller = DenoiseController()
    controller.build_n2n_model(_model_path=_model_path, _model_version=_model_version)

    _noisy_img = load_image(image_path=NOISY_IMAGE_PATH)
    controller.preprocess_image(_source_img=_noisy_img)
    controller.denoise(_type_method=DenoiseMethods.FIRST_NLM)
    _denoised_img = controller.get_result()
    save_image(image=_denoised_img, image_path="1_dendrite.tif")
    # plot_image_slices(controller.noisy_img, cm.jet, X_SCALE, Z_SCALE, np.array(controller.noisy_img.shape) // 2)
    # plot_image_slices(_denoised_img, cm.jet, X_SCALE, Z_SCALE, np.array(_denoised_img.shape) // 2)
    # _images = controller.get_info_images()
    # mid_images = [(_img[0][_images[0][0].shape[0] // 2], _img[1]) for _img in _images]
    # _figures = plot_lines_profile(_images=mid_images, _y_idx=_images[0][0].shape[1] // 2, is_show=True)
