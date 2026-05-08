"""S1-14: Pipeline smoke tests — direct calls to RL core methods (no Pool, no GUI)."""
import os
import sys
import tempfile
import unittest

import numpy as np
from scipy.ndimage import gaussian_filter

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from common.DeconMethods_class import DeconMethods
from common.ImageRaw_class import ImageRaw


# ---------------------------------------------------------------------------
# Shared synthetic data (small enough to be fast)
# ---------------------------------------------------------------------------
def _make_image_and_psf(shape=(8, 32, 32)):
    """Return (image, psf) as float64 3-D arrays."""
    rng = np.random.default_rng(42)
    image = rng.uniform(10, 255, size=shape).astype(np.float64)
    # smooth Gaussian blob as PSF
    psf_raw = np.zeros(shape, dtype=np.float64)
    center = tuple(s // 2 for s in shape)
    psf_raw[center] = 1.0
    psf = gaussian_filter(psf_raw, sigma=1.5)
    psf /= psf.sum()          # normalise
    return image, psf


class TestRLCore(unittest.TestCase):
    """MaxLikelhoodEstimationFFT_3D — Richardson-Lucy base."""

    def setUp(self):
        self.image, self.psf = _make_image_and_psf()

    def test_output_shape_matches_input(self):
        result = DeconMethods.MaxLikelhoodEstimationFFT_3D(
            self.image, self.psf, iterLimit=2, q=None
        )
        self.assertEqual(result.shape, self.image.shape)

    def test_output_is_finite(self):
        result = DeconMethods.MaxLikelhoodEstimationFFT_3D(
            self.image, self.psf, iterLimit=2, q=None
        )
        self.assertTrue(np.isfinite(result).all(), "RL result contains NaN/Inf")

    def test_output_is_non_negative(self):
        result = DeconMethods.MaxLikelhoodEstimationFFT_3D(
            self.image, self.psf, iterLimit=2, q=None
        )
        self.assertGreaterEqual(result.min(), 0.0, "RL result contains negative values")

    def test_input_array_not_mutated(self):
        image_copy = self.image.copy()
        DeconMethods.MaxLikelhoodEstimationFFT_3D(
            self.image, self.psf, iterLimit=2, q=None
        )
        np.testing.assert_array_equal(self.image, image_copy, "RL mutated input array")


class TestRLTVRCore(unittest.TestCase):
    """DeconvolutionRLTVR — RL with Total Variation regularisation."""

    def setUp(self):
        self.image, self.psf = _make_image_and_psf()

    def test_output_shape_matches_input(self):
        result = DeconMethods.DeconvolutionRLTVR(
            self.image, self.psf, lambdaTV=0.0001, iterLimit=2, q=None
        )
        self.assertEqual(result.shape, self.image.shape)

    def test_output_is_finite(self):
        result = DeconMethods.DeconvolutionRLTVR(
            self.image, self.psf, lambdaTV=0.0001, iterLimit=2, q=None
        )
        self.assertTrue(np.isfinite(result).all(), "RLTVR result contains NaN/Inf")

    def test_input_array_not_mutated(self):
        image_copy = self.image.copy()
        DeconMethods.DeconvolutionRLTVR(
            self.image, self.psf, lambdaTV=0.0001, iterLimit=2, q=None
        )
        np.testing.assert_array_equal(self.image, image_copy, "RLTVR mutated input array")


class TestRLTMRCore(unittest.TestCase):
    """DeconvolutionRLTMR — RL with Tikhonov-Miller regularisation."""

    def setUp(self):
        self.image, self.psf = _make_image_and_psf()

    def test_output_shape_matches_input(self):
        result = DeconMethods.DeconvolutionRLTMR(
            self.image, self.psf, lambdaTM=0.00001, iterLimit=2, q=None
        )
        self.assertEqual(result.shape, self.image.shape)

    def test_output_is_finite(self):
        result = DeconMethods.DeconvolutionRLTMR(
            self.image, self.psf, lambdaTM=0.00001, iterLimit=2, q=None
        )
        self.assertTrue(np.isfinite(result).all(), "RLTMR result contains NaN/Inf")


class TestImageRawSaveLoad(unittest.TestCase):
    """load → wrap in ImageRaw → SaveAsTiff round-trip."""

    def test_save_and_reload(self):
        arr = np.random.randint(10, 200, size=(8, 32, 32), dtype=np.uint8)
        voxel = [0.2, 0.089, 0.089]
        img = ImageRaw(voxelSizeIn=voxel, intensitiesIn=arr.astype(np.float64))

        with tempfile.TemporaryDirectory() as tmpdir:
            fpath = os.path.join(tmpdir, "result")
            img.SaveAsTiff(fpath, outtype="uint8")

            saved_files = [f for f in os.listdir(tmpdir) if f.endswith(".tif") or f.endswith(".tiff")]
            self.assertTrue(len(saved_files) > 0, "No tiff file was saved")


if __name__ == "__main__":
    unittest.main()
