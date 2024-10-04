import os
from typing import List

import tifftools
import cv2
import numpy as np
from scipy.ndimage.filters import gaussian_filter, median_filter

BLUR_RAD = (7, 7)


def load_image(image_path: str) -> np.ndarray:
    """Load the source image using the image path."""
    try:
        if image_path is None or not os.path.exists(image_path):
            raise ValueError("Image path cannot be None")
        assert os.path.exists(image_path), f"File not found: {image_path}"
        ret, images = cv2.imreadmulti(image_path, [], cv2.IMREAD_ANYCOLOR)
        assert ret and len(images) > 0, f"Failed to read the source image from path: {image_path}"
        source_img = np.asarray(images)
        return source_img
    except (ValueError, FileNotFoundError, Exception) as e:
        print(f"Error in load_image: {str(e)}")
        raise


def load_images(folder_path: str) -> List[np.ndarray]:
    """Load the images using the folder path."""
    try:
        if folder_path is None or not os.path.exists(folder_path):
            raise ValueError("Image path cannot be None")
        assert os.path.exists(folder_path), f"Folder not found: {folder_path}"
        source_images = []
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(".tif") or filename.lower().endswith(".tiff"):
                image_path = os.path.join(folder_path, filename)
                image = load_image(image_path=image_path)
                source_images.append(image)
        assert source_images, "No TIFF images found in the specified folder."
        return source_images
    except (ValueError, FileNotFoundError, Exception) as e:
        print(f"Error in load_images: {str(e)}")
        raise


def save_image(image: np.ndarray, image_path: str) -> None:
    """Save image to the image path."""
    try:
        if image is None:
            raise ValueError("Image cannot be None")
        if image_path is None:
            raise ValueError("Image path cannot be None")
        if image.ndim == 2:
            cv2.imwrite(image_path, image)
            print("Image saved successfully.")
        elif image.ndim == 3 or image.ndim == 4:
            cv2.imwritemulti(image_path, image)
            print("Image saved successfully.")
    except (ValueError, Exception) as e:
        print(f"Error in save_image: {str(e)}")


def save_images(images: List[np.ndarray], image_names: List[str], folder_path: str) -> None:
    """Save images to the image path."""
    try:
        if images is None:
            raise ValueError("Images cannot be None")
        if image_names is None:
            raise ValueError("Image names cannot be None")

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        for i, image in enumerate(images):
            save_image(image, os.path.join(folder_path, image_names[i]))
        print(f"Images saved to folder: {folder_path}")
    except (ValueError, Exception) as e:
        print(f"Error in save_images: {str(e)}")


def normalize_image(_img: np.ndarray, _bit: int = 8, dtype: str = 'uint8') -> np.ndarray:
    """Normalize an image"""
    max_val = 2 ** _bit - 1
    return np.clip((_img - _img.min()) / (_img.max() - _img.min()) * max_val, 0, max_val).astype(dtype)


def add_poisson_noise(_img: np.ndarray, lambda_val: int) -> np.ndarray:
    noise = np.random.poisson(lambda_val, size=_img.shape).astype("uint8")
    noisy_img = np.clip(_img + noise, 0, 255).astype("uint8")
    return noisy_img


def gauss_blur(_img: np.ndarray, gaussian_sigma: int = 3) -> np.ndarray:
    if _img is None:
        raise ValueError("Image cannot be None")
    if gaussian_sigma is None or gaussian_sigma <= 0:
        raise ValueError("Gaussian sigma cannot be None and must be positive")
    _img = gaussian_filter(_img, sigma=gaussian_sigma)
    return _img


def median_filter_img(_img: np.ndarray, _block_size: int = 3) -> np.ndarray:
    if _img is None:
        raise ValueError("Image cannot be None")
    if _block_size is None or _block_size < 1:
        raise ValueError("Block size cannot be None and must be positive")
    _img = median_filter(_img, size=_block_size)
    return _img


def local_threshold_3d(_img: np.ndarray, _threshold: int = 10,
                       weight: float = 0.05, block_size: int = 3) -> np.ndarray:
    local_median = median_filter(_img, size=block_size)
    threshold = _threshold - weight * (_threshold - local_median)
    output = np.zeros_like(_img)
    output[_img > threshold] = 255

    return output


def maximize_intensity(img: np.ndarray, max_value: int = 255) -> np.ndarray:
    return img / np.amax(img) * max_value


def create_difference_map(_img_1: np.ndarray, _img_2: np.ndarray) -> np.ndarray:
    """Create a difference map between images."""
    try:
        if _img_1 is None:
            raise ValueError("Image cannot be None")
        if _img_2 is None:
            raise ValueError("Image cannot be None")
        difference_map = _img_1.astype(np.float32) - _img_2.astype(np.float32)
        return difference_map
    except Exception as e:
        print(f"Error in create_difference_map: {str(e)}")


def merge_tiff(sources_path: str, target_path: str):
    tiff_files_li = [os.path.join(sources_path, file_name) for file_name in os.listdir(sources_path) if
                     file_name.endswith('.tiff') or file_name.endswith('.tif')]
    tifftools.tiff_concat(tiff_files_li, target_path, overwrite=True)
