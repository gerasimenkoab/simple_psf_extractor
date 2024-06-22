import os
from typing import Tuple, Optional, List
import cv2
import numpy as np

BLUR_RAD = (7, 7)
BIN_THRESH = 0
MAX_BIN_VALUE = 255


class AutoSegmenter:
    def __init__(self):
        self.__source_img = None
        self.__mid_layer_idx = None
        self.__blur_img = None
        self.__bin_img = None
        self.__analysis = None
        self.__bead_centers = None
        self.__thread_area = None
        self.__extracted_beads = None
        self.__averaged_bead = None

    @property
    def source_img(self):
        return self.__source_img

    @property
    def mid_layer_idx(self):
        return self.__mid_layer_idx

    @property
    def blur_img(self):
        return self.__blur_img

    @property
    def analysis(self):
        return self.__analysis

    @property
    def bead_centers(self):
        return self.__bead_centers

    @property
    def extracted_beads(self):
        return self.__extracted_beads

    @property
    def averaged_bead(self):
        return self.__averaged_bead

    def load_image(self, image_path: str) -> None:
        """Load the source image using the image path."""
        try:
            assert image_path, "Source image path is None."
            assert os.path.exists(image_path), f"File not found: {image_path}"
            ret, images = cv2.imreadmulti(image_path, [], cv2.IMREAD_ANYCOLOR)
            assert ret and len(images) > 0, f"Failed to read the source image from path: {image_path}"
            self.__source_img = np.asarray(images)
            self.__mid_layer_idx = self.__source_img.shape[0] // 2
        except (ValueError, FileNotFoundError, Exception) as e:
            print(f"Error in load_image: {str(e)}")
            raise

    def binarize(self, own_img: Optional[np.ndarray] = None, is_show: bool = False) -> np.ndarray:
        """
        Binarize the loaded source image.
        Parameters:
            own_img (Optional[np.ndarray]): An optional custom source image to be binarized.
            is_show (bool): If True, displays the original and binarized images using OpenCV.
        Returns:
            np.ndarray: The binarized image as a NumPy array.
        """
        try:
            if own_img is not None:
                print(own_img.shape, own_img.shape[0])
                self.__source_img = np.asarray(own_img)
                self.__mid_layer_idx = self.__source_img.shape[0] // 2
                print(self.__mid_layer_idx)

            # Ensure the source image and mid layer are valid
            assert self.__source_img is not None and len(
                self.__source_img) > 0, "Source image is None. Run load_image first."
            assert self.__mid_layer_idx < len(self.__source_img), "Mid layer index out of bounds."

            # Convert the middle layer to grayscale
            mono_img = self.__source_img[self.__mid_layer_idx].astype(np.uint8)
            self.__blur_img = cv2.GaussianBlur(mono_img, BLUR_RAD, 0)
            self.__bin_img = cv2.threshold(
                self.__blur_img, BIN_THRESH, MAX_BIN_VALUE, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
            )[1]
            self.__bin_img = cv2.bitwise_not(self.__bin_img)

            if is_show:
                cv2.imshow("Image", self.__source_img[self.__mid_layer_idx])
                cv2.imshow("Binarized image", self.__bin_img)
                cv2.waitKey(0)

            return self.__bin_img
        except Exception as e:
            print(f"Error in binarize: {str(e)}")
            raise

    def find_bead_centers(self, max_area: int = 500) -> np.ndarray:
        """
        Find bead centers in the binarized image.
        Parameters:
            max_area (int): The maximum area allowed for a bead.
        Returns:
            np.ndarray: Centroid coordinates of detected bead centers.
        """
        try:
            # assert self.__blur_img, "Blur image is None. Run binarize first."
            assert self.__bin_img is not None, "Binarized image is None. Run binarize first."
            assert max_area >= 0, "Max area cannot be negative."

            self.__analysis = cv2.connectedComponentsWithStats(self.__bin_img, 4, cv2.CV_32S)
            (total_labels, _, _, centroid) = self.__analysis
            self.__thread_area = max_area
            bead_centers = np.array([centroid[i - 1] for i in range(1, total_labels) if self.__is_correct_bead(i - 1)],
                                    dtype=int)

            if len(centroid) > 1:
                self.__bead_centers = np.array([centroid[i - 1] for i in range(1, total_labels)
                                                if self.__is_correct_bead(i - 1)], dtype=int)
                return bead_centers
            else:
                raise Exception("No connected components found in the image.")

        except (ValueError, Exception) as e:
            print(f"Error in find_bead_centers: {str(e)}")
            raise

    def __is_correct_bead(self, bead_idx: int) -> bool:
        """
        Check if a given bead is correct based on area
        Parameters:
            bead_idx (int): Index of the detected beads(analysis) to be checked.
        """
        try:
            assert self.__thread_area > 0, "Max area cannot be negative."
            assert self.__analysis, "Analysis is None. Run binarize find_bead_centers."
            assert bead_idx >= 0, "Bead index cannot be negative."

            (_, _, values, _) = self.__analysis
            area = values[bead_idx, cv2.CC_STAT_AREA]
            return 0 < area < self.__thread_area

        except (ValueError, Exception) as e:
            print(f"Error in __is_correct_bead: {str(e)}")
            raise

    def extract_beads(self, box_size: int) -> Tuple[List[np.ndarray], np.ndarray]:
        """
        Extract beads based on bead centers and box size.
        Parameters:
            box_size (int): Size of the bounding box for extracting beads.
        Returns:
            Tuple[List[np.ndarray], np.ndarray]: A tuple with the list of extracted beads and updated bead centers.
        """
        try:
            assert box_size > 0, "Max area cannot be negative."
            assert self.__source_img, "Source image is None. Run binarize load_image."
            assert self.__bead_centers, "Bead centers is None. Run binarize find_bead_centers."
            self.__extracted_beads = []
            valid_centers = []
            for center in self.__bead_centers:
                bead = self.extract_single_bead(center=center, bound_size=box_size, is_weak_check=False)
                if bead is not None:
                    self.__extracted_beads.append(bead)
                    valid_centers.append(center)
            self.__bead_centers = np.array(valid_centers, dtype=int)
            return self.__extracted_beads, self.__bead_centers

        except (ValueError, Exception) as e:
            print(f"Error in extract_beads: {str(e)}")
            raise

    def extract_single_bead(self, center: Tuple[int, int], bound_size: int, is_weak_check: bool) \
            -> Optional[np.ndarray]:
        """Extract a single bead based on its center coordinates."""
        try:
            assert self.__source_img, "Source image is None. Run binarize load_image."
            assert center, "Center coordinates is None."

            bound1, bound2, bound3, bound4 = self.get_bounds(center=center, bound_size=bound_size,
                                                             img=self.__source_img, is_weak_check=is_weak_check)
            single_bead = self.__source_img[:, bound1:bound2, bound3:bound4]
            if is_weak_check or self.__is_within_bounds(center, bound_size):
                return single_bead if single_bead is not None else None
            else:
                return None

        except (ValueError, Exception) as e:
            print(f"Error in extract_single_bead: {str(e)}")
            raise

    @staticmethod
    def get_bounds(center: Tuple[int, int], bound_size: int, img: np.ndarray, is_weak_check: bool) -> (
            Tuple)[int, int, int, int]:
        """
        Get the bounding box coordinates around a given center.
        Parameters:
            center (Tuple[int, int]): The bead center coordinates (x, y).
            bound_size (int): The size of the bounding box.
            img (np.ndarray): The input image.
            is_weak_check (bool): If True, weakly checks that the bounding box stays within image boundaries.
        Returns:
            Tuple[int, int, int, int]: The bounding box coordinates (y_min, y_max, x_min, x_max).
        """
        try:
            x, y = center
            x_idx, y_idx = 2 if len(img.shape) == 4 else 1, 1 if len(img.shape) == 4 else 0
            if is_weak_check:
                return (max(0, int(y - bound_size // 2)), min(img.shape[y_idx], int(y + bound_size // 2)),
                        max(0, int(x - bound_size // 2)), min(img.shape[x_idx], int(x + bound_size // 2)))
            else:
                return int(y - bound_size // 2), int(y + bound_size // 2), int(x - bound_size // 2), int(
                    x + bound_size // 2)
        except (ValueError, Exception) as e:
            print(f"Error in __get_bounds: {str(e)}")
            raise

    def __is_within_bounds(self, center: Tuple[int, int], bound_size: int) -> bool:
        """Check if a given bead center is within the bounds of the source image."""
        try:
            x, y = center
            assert x > 0 and y > 0, "Center coordinates cannot be negative."
            assert self.__source_img, "Source image is None. Run binarize load_image."
            assert bound_size, "Bound size is None."
            return (bound_size // 2 <= y < self.__source_img.shape[1] - bound_size // 2
                    and bound_size // 2 <= x < self.__source_img.shape[2] - bound_size // 2)
        except (ValueError, Exception) as e:
            print(f"Error in __is_within_bounds: {str(e)}")
            raise

    def average_bead(self, is_show: bool = False) -> np.ndarray:
        """Calculate and show the average bead."""
        try:
            assert self.__extracted_beads, "Extracted beads is None. Run binarize extract_beads."
            self.__averaged_bead = np.mean(self.__extracted_beads, axis=0).astype("uint8")
            if is_show:
                cv2.imshow("Averaged bead", self.__averaged_bead)
                cv2.waitKey(0)
            return self.__averaged_bead
        except (ValueError, Exception) as e:
            print(f"Error in average_bead: {str(e)}")
