"""S1-15: Mini regression tests — edge cases for shape and numerical stability."""
import os
import sys
import unittest

import numpy as np
from scipy.ndimage import gaussian_filter

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from common.DeconMethods_class import DeconMethods


def _gauss_psf(shape):
    psf_raw = np.zeros(shape, dtype=np.float64)
    center = tuple(s // 2 for s in shape)
    psf_raw[center] = 1.0
    psf = gaussian_filter(psf_raw, sigma=1.0)
    psf /= psf.sum()
    return psf


# ---------------------------------------------------------------------------
# Edge case: image with NaN values — pre-processing must handle them
# ---------------------------------------------------------------------------
class TestNaNInputHandling(unittest.TestCase):
    def _image_with_nan(self, shape=(6, 16, 16)):
        rng = np.random.default_rng(7)
        img = rng.uniform(10, 200, size=shape)
        img[0, 0, 0] = np.nan
        img[1, 2, 3] = np.nan
        return img

    def test_RL_survives_nan_input(self):
        img = self._image_with_nan()
        psf = _gauss_psf(img.shape)
        result = DeconMethods.MaxLikelhoodEstimationFFT_3D(img, psf, iterLimit=2, q=None)
        self.assertEqual(result.shape, img.shape)
        self.assertTrue(np.isfinite(result).all())

    def test_RLTMR_survives_nan_input(self):
        img = self._image_with_nan()
        psf = _gauss_psf(img.shape)
        result = DeconMethods.DeconvolutionRLTMR(img, psf, lambdaTM=0.00001, iterLimit=2, q=None)
        self.assertEqual(result.shape, img.shape)
        self.assertTrue(np.isfinite(result).all())

    def test_RLTVR_survives_nan_input(self):
        img = self._image_with_nan()
        psf = _gauss_psf(img.shape)
        result = DeconMethods.DeconvolutionRLTVR(img, psf, lambdaTV=0.0001, iterLimit=2, q=None)
        self.assertEqual(result.shape, img.shape)
        self.assertTrue(np.isfinite(result).all())


# ---------------------------------------------------------------------------
# Edge case: near-zero image (all values close to floor)
# ---------------------------------------------------------------------------
class TestNearZeroInput(unittest.TestCase):
    def test_RL_near_zero_image(self):
        img = np.full((6, 16, 16), 1e-10, dtype=np.float64)
        psf = _gauss_psf(img.shape)
        result = DeconMethods.MaxLikelhoodEstimationFFT_3D(img, psf, iterLimit=2, q=None)
        self.assertEqual(result.shape, img.shape)
        self.assertTrue(np.isfinite(result).all())

    def test_RLTVR_near_zero_image(self):
        img = np.full((6, 16, 16), 1e-10, dtype=np.float64)
        psf = _gauss_psf(img.shape)
        result = DeconMethods.DeconvolutionRLTVR(img, psf, lambdaTV=0.0001, iterLimit=2, q=None)
        self.assertEqual(result.shape, img.shape)
        self.assertTrue(np.isfinite(result).all())


# ---------------------------------------------------------------------------
# Edge case: non-square / non-cubic shapes
# ---------------------------------------------------------------------------
class TestNonCubicShapes(unittest.TestCase):
    def test_RL_rectangular_shape(self):
        shape = (4, 10, 20)
        rng = np.random.default_rng(99)
        img = rng.uniform(10, 200, size=shape)
        psf = _gauss_psf(shape)
        result = DeconMethods.MaxLikelhoodEstimationFFT_3D(img, psf, iterLimit=2, q=None)
        self.assertEqual(result.shape, shape)

    def test_RLTVR_rectangular_shape(self):
        shape = (4, 10, 20)
        rng = np.random.default_rng(99)
        img = rng.uniform(10, 200, size=shape)
        psf = _gauss_psf(shape)
        result = DeconMethods.DeconvolutionRLTVR(img, psf, lambdaTV=0.0001, iterLimit=2, q=None)
        self.assertEqual(result.shape, shape)

    def test_RLTMR_rectangular_shape(self):
        shape = (4, 10, 20)
        rng = np.random.default_rng(99)
        img = rng.uniform(10, 200, size=shape)
        psf = _gauss_psf(shape)
        result = DeconMethods.DeconvolutionRLTMR(img, psf, lambdaTM=0.00001, iterLimit=2, q=None)
        self.assertEqual(result.shape, shape)


# ---------------------------------------------------------------------------
# Edge case: single iteration (iterLimit=1)
# ---------------------------------------------------------------------------
class TestSingleIteration(unittest.TestCase):
    def setUp(self):
        shape = (6, 16, 16)
        rng = np.random.default_rng(3)
        self.img = rng.uniform(10, 200, size=shape)
        self.psf = _gauss_psf(shape)

    def test_RL_single_iter(self):
        result = DeconMethods.MaxLikelhoodEstimationFFT_3D(self.img, self.psf, iterLimit=1, q=None)
        self.assertEqual(result.shape, self.img.shape)
        self.assertTrue(np.isfinite(result).all())

    def test_RLTVR_single_iter(self):
        result = DeconMethods.DeconvolutionRLTVR(self.img, self.psf, lambdaTV=0.0001, iterLimit=1, q=None)
        self.assertEqual(result.shape, self.img.shape)
        self.assertTrue(np.isfinite(result).all())

    def test_RLTMR_single_iter(self):
        result = DeconMethods.DeconvolutionRLTMR(self.img, self.psf, lambdaTM=0.00001, iterLimit=1, q=None)
        self.assertEqual(result.shape, self.img.shape)
        self.assertTrue(np.isfinite(result).all())


# ---------------------------------------------------------------------------
# Edge case: DeconImage input validation (bad params must raise ValueError)
# ---------------------------------------------------------------------------
class TestDeconImageInputValidation(unittest.TestCase):
    def _make_valid(self):
        shape = (4, 8, 8)
        rng = np.random.default_rng(5)
        img = rng.uniform(10, 200, size=shape)
        psf = _gauss_psf(shape)
        return img, psf

    def test_raises_on_iternum_zero(self):
        img, psf = self._make_valid()
        with self.assertRaises(ValueError):
            DeconMethods.DeconImage(img, psf, iterNum=0, deconType="RL", lambdaR=0)

    def test_raises_on_2d_image(self):
        img = np.ones((10, 10), dtype=np.float64)
        psf = np.ones((3, 3), dtype=np.float64)
        with self.assertRaises(ValueError):
            DeconMethods.DeconImage(img, psf, iterNum=1, deconType="RL", lambdaR=0)


if __name__ == "__main__":
    unittest.main()
