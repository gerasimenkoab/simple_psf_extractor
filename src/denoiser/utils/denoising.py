import math
import time
from typing import Dict, Tuple

import numpy as np
from skimage.metrics import peak_signal_noise_ratio
from ..n2n.controller import DenoiseMethods, DenoiseController


def calculate_image_stats(_clean_img: np.ndarray, _denoised_img: np.ndarray) -> Tuple[Dict[str, float], str]:
    try:
        if _clean_img is None:
            raise ValueError("No clean image")
        if _denoised_img is None:
            raise ValueError("No denoised image")

        psnr = peak_signal_noise_ratio(_clean_img, _denoised_img, data_range=255)
        mse = np.mean((_clean_img - _denoised_img) ** 2) / (_clean_img.max() ** 2)

        stats = {'psnr': psnr, 'mse': mse}
        stats_str = f"PSNR: {psnr:.4f}; MSE: {mse:.4f}\n"
        return stats, stats_str
    except Exception as e:
        raise ValueError(f"Error in calculate_image_stats: {str(e)}")


def measure_time_execution(_controller: DenoiseController,  _type_method: DenoiseMethods.FIRST_NLM) -> float:
    start_time = time.time()
    _controller.denoise(_type_method=_type_method)
    end_time = time.time()
    processing_time = end_time - start_time
    print(f"Denoising({_type_method.value}), Processing Time: {processing_time} seconds")
    return processing_time
