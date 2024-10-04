import os
import random
import typing as tp
from typing import Tuple, List, Union, Optional

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import AxesGrid



ImageInfo = Tuple[Union[np.ndarray, plt.Figure], str]  # image, label
LineInfo = Tuple[List[int], List[int], str, Optional[str]]  # x_values, y_values, label, color
PlotInfo = Tuple[str, Optional[str], Optional[Tuple[str, str]]]  # title, special_info, x_label, y_label


def show_images(_images: List[ImageInfo], _info: PlotInfo, is_show: bool = False, cmap: str = 'default') -> plt.Figure:
    if _images is None:
        raise ValueError("Images cannot be empty")
    fig, axes = plt.subplots(1, len(_images), figsize=(5 * len(_images), 5))
    colorbar_fig = None

    vmin, vmax = 255, 0
    for ax, (img, title) in zip(axes, _images):
        if isinstance(img, plt.Figure):
            if np.amin(img.get_axes()[0].get_images()[0].get_array()) < vmin:
                vmin = np.amin(img.get_axes()[0].get_images()[0].get_array())
            if np.amax(img.get_axes()[0].get_images()[0].get_array()) > vmax:
                vmax = np.amax(img.get_axes()[0].get_images()[0].get_array())

    for ax, (img, title) in zip(axes, _images):
        if isinstance(img, plt.Figure):
            fig_im = img.get_axes()[0].get_images()[0]
            ax.imshow(fig_im.get_array(), cmap='jet', vmin=vmin, vmax=vmax)
        else:
            if cmap == 'jet':
                im = ax.imshow(img, cmap='jet', vmin=np.min(img), vmax=np.max(img))
                plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            else:
                ax.imshow(img, cmap='gray' if cmap == 'default' else cmap)
        ax.set_title(title)
        if isinstance(img, plt.Figure):
            colorbar_fig = img

    main_title, legend, _ = _info
    fig.suptitle(main_title)
    if legend is not None:
        fig.text(0.5, 0.01, legend, horizontalalignment='center', fontsize=8)
    if colorbar_fig is not None:
        plt.colorbar(colorbar_fig.get_axes()[0].images[0], ax=axes.ravel().tolist(), fraction=0.046, pad=0.04)
    if is_show:
        plt.show()
    return fig


def generate_2d_projections(_img: np.ndarray, _fig_size: Tuple[int, int] = None, _title: str = None,
                            _is_show: bool = False, _filename: str = None, _save_folder: str = None) -> plt.Figure:
    """Generate 2D projections (xy, xz, yz) and optionally display them and save to file."""
    try:
        if _img is None:
            raise ValueError("Image cannot be empty")
        if len(_img.shape) == 3:
            result = np.where(_img == np.amax(_img))
            projections_coord = [result[0][0], result[1][0], result[2][0]]
            fig, axs = plt.subplots(3, 1, sharex=False, figsize=_fig_size if _fig_size is not None else (2, 6))

            for i, ax in enumerate(axs):
                ax.imshow(_img[:, :, projections_coord[i]], cmap='jet', vmin=np.min(_img), vmax=np.max(_img))
                ax.set_title(['XY Projection', 'XZ Projection', 'YZ Projection'][i])
        else:
            fig, ax = plt.subplots(1, 1, figsize=_fig_size if _fig_size is not None else (4, 4))
            im = ax.imshow(_img, cmap='jet', vmin=np.min(_img), vmax=np.max(_img))
            plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            if _title is not None:
                title = f'{_title}, XY Projection'
                ax.set_title(title)

        if _save_folder is not None and _filename is not None:
            if _title is not None:
                title = _title.lower().replace(':', '_').replace(' ', '_').replace('-', '_')
                filename = f'{_filename}_{title}'
            else:
                filename = f'{_filename}_2d_projections.png'
            save_graphic(fig=fig, graphic_filename=filename, graphics_folder=_save_folder)
        if _is_show:
            plt.show()
        return fig
    except Exception as e:
        print(f"Error in generate_2d_projections: {str(e)}")


def plot_dif_maps(_dif_maps: List[np.ndarray], _info: PlotInfo, _is_show: bool = False) -> plt.Figure:
    images = []
    for idx, dif_map in enumerate(_dif_maps):
        title = f"Difference Map {idx+1}"
        images.append((generate_2d_projections(_img=dif_map, _is_show=False), title))
    fig = show_images(_images=images, _info=_info, is_show=_is_show, cmap='jet')
    return fig


def save_graphic(fig: plt.Figure, graphic_filename: str, graphics_folder: str) -> None:
    try:
        if graphics_folder is None:
            raise ValueError("Graphics folder cannot be empty")
        if fig is None:
            raise ValueError("Figure cannot be empty")
        if graphic_filename is None:
            raise ValueError("Graphic filename cannot be empty")
        os.makedirs(graphics_folder, exist_ok=True)
        filename = os.path.join(graphics_folder, graphic_filename)
        fig.savefig(filename)
        print(f"Saved image to {filename}")
    except Exception as e:
        print(f"Error in save_graphic: {str(e)}")


def plot_intensity_histograms(_images: List[ImageInfo], is_show: bool = False) -> plt.Figure:
    num_bins = 256
    fig, ax = plt.subplots(figsize=(8, 6))
    existing_colors = set()
    max_range = int(max(img[0].max() for img, _ in _images))
    for i, (img, title) in enumerate(_images):
        flattened_image = img.flatten()
        color = generate_color(_existing_colors=existing_colors)
        existing_colors.add(color)
        counts, bins = np.histogram(flattened_image)
        ax.hist(flattened_image, bins=bins, range=(0, max_range), color=color, alpha=0.5, label=title)

    ax.set_title('Intensity Histograms')
    ax.set_xlabel('Intensity')
    ax.set_ylabel('Frequency')
    ax.grid(True)
    ax.legend()
    if is_show:
        plt.show()
    return fig


def line_profile(_img: ImageInfo, _y_idx: int, ax: plt.Axes = None) -> plt.Figure:
    if ax is None:
        fig, ax = plt.subplots(2, 1, figsize=(8, 8))
    else:
        fig = ax[0].figure
    x = np.arange(0, _img[0].shape[0])
    y = _img[0][_y_idx, :]

    ax[0].imshow(_img[0], cmap='gray')
    ax[0].set_title(_img[1])
    ax[0].plot([0, _img[0].shape[0] - 1], [_y_idx, _y_idx], color='red')
    ax[0].axis('off')

    ax[1].plot(x, y, color='red')
    ax[1].set_xlabel('Pixel')
    ax[1].set_ylabel('Intensity')
    ax[1].set_title(f'Line Profile - {_img[1]}')
    ax[1].grid(True)

    return fig


def plot_lines_profile(_images: List[ImageInfo], _y_idx: int, is_show: bool = False) -> plt.Figure:
    num_images = len(_images)
    fig, ax = plt.subplots(2, num_images, figsize=(8*num_images, 8))
    for i, img_info in enumerate(_images):
        line_profile(_img=img_info, _y_idx=_y_idx, ax=ax[:, i])
    plt.tight_layout()
    if is_show:
        plt.show()
    return fig


def draw_lines(_lines: List[LineInfo], _info: PlotInfo, _marker: str = 'o', is_show: bool = False) -> plt.Figure:
    fig, ax = plt.subplots()
    existing_colors = set()
    for (x_values, y_values, label, custom_color) in _lines:
        color = custom_color if custom_color else generate_color(existing_colors)
        existing_colors.add(color)
        ax.plot(x_values, y_values, marker=_marker, color=color, label=label)
    title, _, (x_label, y_label) = _info
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.legend()
    ax.grid(True)

    if is_show:
        plt.show()
    return fig


def generate_color(_existing_colors: set) -> str:
    """
    Generate a new color that is not already in the set of existing colors.
    Args:
        _existing_colors (set): Set of existing colors.
    Returns:
        str: A new color.
    """
    all_colors = ['b', 'g', 'r', 'k', 'm', 'y', 'c']
    available_colors = set(all_colors) - _existing_colors
    if available_colors:
        return random.choice(list(available_colors))
    else:
        raise ValueError("No available colors left to choose from.")


def get_row_plane(img: np.ndarray, row: int) -> np.ndarray:
    layers, rows, cols = img.shape[0], img.shape[1], img.shape[2]
    plane = np.ndarray([layers, cols])
    plane[:, :] = img[:, row, :]
    return plane


def get_col_plane(img: np.ndarray, column: int) -> np.ndarray:
    layers, rows, cols = img.shape[0], img.shape[1], img.shape[2]
    plane = np.ndarray([layers, rows])
    plane[:, :] = img[:, :, column]
    return plane


def get_layer_plane(img: np.ndarray, layer: int) -> np.ndarray:
    layers, rows, cols = img.shape[0], img.shape[1], img.shape[2]
    plane = np.ndarray([rows, cols])
    plane[:, :] = img[layer, :, :]
    return plane


def generate_image_slices(
        img: np.ndarray,
        cmap,
        xy_resolution: float,
        z_resolution: float,
        coords: tp.Tuple[int] = [0, 0, 0],
        scale_borders: tp.Tuple[int] | None = None,
        is_show: bool = False
) -> plt.Figure:
    plane_row, plane_col, plane_layer = (
        get_row_plane(img, coords[1]),
        get_col_plane(img, coords[2]),
        get_layer_plane(img, coords[0]),
    )

    if scale_borders == None:
        scale_borders = [0, 0]
        scale_borders[0] = min(
            np.amin(plane_row), np.amin(plane_layer), np.amin(plane_col)
        )
        scale_borders[1] = max(
            np.amax(plane_row), np.amax(plane_layer), np.amax(plane_col)
        )

    aspect_value_xz = z_resolution / xy_resolution  # (img.shape[0] * z_resolution) / (img.shape[1] * xy_resolution) * 2
    aspect_value_yz = xy_resolution / z_resolution  # (img.shape[2] * xy_resolution) / (img.shape[0] * z_resolution) / 2

    plt_width = (np.array(img).shape[0] + np.array(img).shape[2]) / 25
    plt_height = (np.array(img).shape[0] + np.array(img).shape[1]) / 25
    fig = plt.figure(figsize=(plt_width, plt_height))

    grid = AxesGrid(
        fig,
        111,
        nrows_ncols=(2, 2),
        axes_pad=0.05,
        cbar_mode="single",
        cbar_location="right",
        cbar_pad=0.1,
    )

    grid[0].set_axis_off()

    grid[1].set_axis_off()
    grid[1].set_label("X-Z projection")
    im_main = grid[1].imshow(
        plane_row,
        cmap=cmap,
        vmin=scale_borders[0],
        vmax=scale_borders[1],
        aspect=(aspect_value_xz),
    )

    grid[2].set_axis_off()
    grid[2].set_label("Y-Z projection")
    plane_col = plane_col.transpose()
    im = grid[2].imshow(
        plane_col,
        cmap=cmap,
        vmin=scale_borders[0],
        vmax=scale_borders[1],
        aspect=aspect_value_yz,
    )

    grid[3].set_axis_off()
    grid[2].set_label("X-Y projection")
    im_main = grid[3].imshow(
        plane_layer, cmap=cmap, vmin=scale_borders[0], vmax=scale_borders[1]
    )

    cbar = grid.cbar_axes[0].colorbar(im_main)
    if is_show:
        plt.show()
    return fig


def plot_image_slices(
        img: np.ndarray,
        cmap,
        xy_resolution: float,
        z_resolution: float,
        coords: tp.Tuple[int] = [0, 0, 0],
        scale_borders: tp.Tuple[int] | None = None
) -> None:
    generate_image_slices(img, cmap, xy_resolution, z_resolution, coords, scale_borders)
    plt.show()
    return
