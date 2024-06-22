import math
from typing import Any, Tuple, Optional, List, Union

import cv2
import numpy as np
from matplotlib import pyplot as plt

from AutoSegmentation.utils.segm_analysis import SegmAnalysis
from AutoSegmentation.segmenter.config import source_image_path, marked_bead_path
from AutoSegmentation.utils.exceptions import check_positive_integer, check_not_none
from AutoSegmentation.segmenter.auto_segmenter import AutoSegmenter


COLOR = (255, 0, 0)
THICKNESS = 2


class Controller:
    def __init__(self):
        self.__auto_segm = AutoSegmenter()
        self.__source_img = None
        self.__mid_layer = None
        self.__analysis = None
        self.__avg_bead = None
        self.__marked_beads_img = None
        self.__opt_bound_size = None
        self.__segm_analysis = SegmAnalysis(auto_segm=self.__auto_segm)
        self.__2d_projections = None

    @property
    def source_img(self):
        return self.__source_img

    @property
    def mid_layer(self):
        return self.__mid_layer

    @property
    def analysis(self):
        return self.__analysis

    @property
    def avg_bead(self):
        return self.__avg_bead

    @property
    def projections(self):
        return self.__2d_projections

    @property
    def marked_beads_img(self):
        return self.__marked_beads_img

    def init_auto_segm(self, image: Union[str, np.ndarray]):
        if isinstance(image, str):
            self.__auto_segm.load_image(image_path=image)

        else:
            self.__auto_segm.binarize(own_img=image if isinstance(image, np.ndarray) else None, is_show=False)
        self.__source_img = self.__auto_segm.source_img
        self.__mid_layer = self.__auto_segm.mid_layer_idx

    def segment_beads(self, max_area: int = 500, box_size: int = 36):
        self.__auto_segm.binarize(own_img=None, is_show=False)
        self.__auto_segm.find_bead_centers(max_area=max_area)
        self.__auto_segm.extract_beads(box_size=box_size)
        self.__analysis = self.__auto_segm.analysis

    def average_bead(self) -> None:
        self.__avg_bead = self.__auto_segm.average_bead()
        self.__2d_projections = self.__segm_analysis.generate_2d_projections()

    def mark_bead(self, coords: Tuple[int, int], box_size: int):
        try:
            x, y = coords
            half_size = box_size // 2
            top_left = (x - half_size, y - half_size)
            bottom_right = (x + half_size, y + half_size)
            cv2.rectangle(
                self.__marked_beads_img,
                top_left,
                bottom_right,
                color=COLOR,
                thickness=THICKNESS,
            )
        except (ValueError, Exception) as e:
            print(f"Error in mark_bead: {str(e)}")

    def mark_beads(self, box_size: int, is_show: bool = False) -> np.ndarray:
        """Mark beads on the source image."""
        try:
            check_not_none(value=self.__auto_segm.source_img, name="Source image", func_name="load_image")
            check_not_none(value=self.__auto_segm.bead_centers, name="Bead centers", func_name="find_bead_centers")
            check_positive_integer(value=box_size, name="Box size")

            self.__marked_beads_img = self.__auto_segm.source_img[self.__auto_segm.mid_layer_idx].copy()
            for center in self.__auto_segm.bead_centers:
                self.mark_bead(coords=center, box_size=box_size)

            if is_show:
                cv2.imshow("Marked Beads", self.__marked_beads_img)
                cv2.waitKey(0)
            return self.__marked_beads_img

        except (ValueError, Exception) as e:
            print(f"Error in mark_beads: {str(e)}")

    def find_opt_bound_size(self) -> tuple[int | Any, tuple, int]:
        """
        Find the optimal bound size using the third and fourth components (width and height) of the analysis from blur_img.
        Returns the index, centroid coordinates, and maximum area of the optimal bound size.
        """
        try:
            check_not_none(value=self.__auto_segm.analysis, name="Analysis", func_name="find_bead_centers")

            (total_labels, _, values, centroid) = self.__auto_segm.analysis
            assert total_labels > 1, "No connected components found in the image."

            third_component_values = values[1:, 2]
            fourth_component_values = values[1:, 3]
            opt_bound_idx = np.argmax(third_component_values + fourth_component_values) + 1
            opt_bound_center = centroid[opt_bound_idx - 1]
            opt_bound_value = max(values[opt_bound_idx, 3], values[opt_bound_idx, 2])
            return opt_bound_idx, tuple(opt_bound_center), int(opt_bound_value)

        except (ValueError, Exception) as e:
            print(f"Error in find_opt_bound_size: {str(e)}")
            raise

    def __find_nearest_center(self, box_size: int, source_coords: Tuple[int, int]) -> Tuple[int, int]:
        """
        Find the index of the bead with the maximum intensity in the connected component.
        """
        try:
            check_not_none(value=box_size, name="Box size")
            check_not_none(value=self.__auto_segm.blur_img, name="Analysis", func_name="binarize")

            bound1, bound2, bound3, bound4 = self.__auto_segm.get_bounds(center=source_coords, bound_size=box_size,
                                                                         img=self.__auto_segm.blur_img,
                                                                         is_weak_check=True)

            if bound1 >= bound2 or bound3 >= bound4:
                raise ValueError("Invalid bounds after adjustment.")

            region = self.__auto_segm.blur_img[bound1:bound2, bound3:bound4]
            coords_within_region = np.unravel_index(np.argmax(region), region.shape)
            coords = (coords_within_region[1] + bound3, coords_within_region[0] + bound1)
            return coords

        except Exception as e:
            print(f"Error in find_nearest_center: {str(e)}")

    def user_center_feedback(self, box_size: int, source_coords: Tuple[int, int]) -> tuple[int, str, Optional[np.ndarray]]:
        """
        Obtain user feedback on the detected bead nearest to the specified coordinates.
        This method for user experience(to communicate with GUI)
        """
        try:
            check_not_none(value=box_size, name="Box size")
            coords = self.__find_nearest_center(box_size=box_size, source_coords=source_coords)
            half_size = box_size // 2
            (_, _, _, centroid) = self.__auto_segm.analysis
            bead_idx = np.argmin(np.linalg.norm(centroid - np.array(coords), axis=1))
            bead_idx_local = np.argmin(np.linalg.norm(self.__auto_segm.bead_centers - np.array(coords), axis=1))
            thread_norm = half_size * math.sqrt(2)
            opt_bound = self.__opt_bound_size
            bv = self.__auto_segm.extract_single_bead(center=coords, bound_size=opt_bound, is_weak_check=True)

            if bv is None:
                return -1, 'not-bead', None
            bead_values = bv.flatten().tolist() if bv is not None else None
            if (np.linalg.norm(centroid[bead_idx] - np.array(coords)) > thread_norm) or (bv.shape[1] != opt_bound or bv.shape[2] != opt_bound):
                return -1, 'not-bead', bead_values
            elif np.linalg.norm(self.__auto_segm.bead_centers[bead_idx_local] - np.array(coords)) > thread_norm:
                return bead_idx, 'incorrect', bead_values
            else:
                return bead_idx, 'correct', bead_values

        except Exception as e:
            print(f"Error in user_center_feedback: {str(e)}")

    def manual_mark(self, new_coords: List[Tuple[int, int]]):
        try:
            _, _, self.__opt_bound_size = self.find_opt_bound_size()
            if new_coords is None:
                raise Exception("new_coords is not available.")
            not_beads, correct_beads, incorrect_beads = [], [], []

            for coord in new_coords:
                bead_idx, bead_type, bead_values = self.user_center_feedback(box_size=self.__opt_bound_size,
                                                                             source_coords=coord)
                if bead_type == 'not-bead' or bead_values is None:
                    not_beads.append(bead_values)
                elif bead_type == 'incorrect':
                    correct_beads.append(bead_values)
                elif bead_type == 'correct':
                    incorrect_beads.append(bead_values)
                else:
                    print("Not corrected bead_type")

            return not_beads, correct_beads, incorrect_beads
        except Exception as e:
            print(f"Error in manual_mark: {str(e)}")


if __name__ == "__main__":
    controller = Controller()
    controller.init_auto_segm(image=source_image_path)
    controller.segment_beads(max_area=500, box_size=36)
    controller.average_bead()
    controller.mark_beads(box_size=36, is_show=True)
    (_, _, _, centroid) = controller.analysis
    not_beads, correct_beads, incorrect_beads = controller.manual_mark(new_coords=centroid)
    print(len(not_beads), len(correct_beads), len(incorrect_beads))
    print(len(not_beads[0]))
    print(len(correct_beads[0]))
    print(len(incorrect_beads[0]))
