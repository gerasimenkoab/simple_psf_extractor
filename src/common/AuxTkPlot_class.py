from typing import Tuple, Any

import numpy as np
import io
from PIL import Image
from matplotlib import pyplot as plt
import matplotlib.ticker as plticker
import matplotlib.cm as cm



class AuxCanvasPlot():
    """Class for creation image for tkinter with matplotlib and PIL """

    @staticmethod
    def FigureFrom3DArray(arr3D: np.ndarray, plotName:str = None, widthPt=100, heightPt = 300, dpiIn = 300)->plt.Figure:
        """Function create matplotlib.figure.Figure  object of figure with 3 slices of 3D array using matplotlib.
        
        Input: arr3d - 3d ndarray
               plotName - plot header name
        Returns:
                matplotlib.figure.Figure  object
                
        """
        if arr3D.ndim != 3:
            raise ValueError("Not a 3D array recieved.", "wrong-array-dimensions")
        maxIntensity = np.amax(arr3D) #255
        cmap = cm.gist_earth #plasma, gnuplot, gist_earth, CMRmap, inferno, magma, viridis
        dpiSet = dpiIn
        widthInch = widthPt / dpiSet
        heightInch = heightPt * 1.02 / dpiSet
        # widthInch = 1.5
        # heightInch = 4.5
        # creating figure with matplotlib
        fig, axs = plt.subplots(nrows=3, sharex=False, figsize=(widthInch, heightInch),dpi = dpiSet, layout="constrained")
        
        #fig.subplots_adjust(left=0.01, right=0.1)  # Adjust subplot position not compatible with  layout="constrained"
        if plotName is not None:
            fig.suptitle(plotName)
        else:
            fig.suptitle(" ")
        loc = plticker.MultipleLocator(base=10.0)  # ticks step setup
        labelFontSize = int(dpiIn /50)
        tickFontSize = labelFontSize - 1
        i = 0
        axs[i].set_xlabel("x(pt)",fontsize = labelFontSize)
        axs[i].set_ylabel("y(pt)",fontsize = labelFontSize, rotation=0)
        axs[i].xaxis.set_label_coords(1.0, -0.1)  # Adjust corresponding label coordinates relative to the axes
        axs[i].yaxis.set_label_coords(-0.15, 1.05)  # Adjust corresponding label coordinates relative to the axes
        axs[i].tick_params(axis='both', which='major',labelrotation=0, labelsize=tickFontSize)
        axs[i].set_xlim(0, arr3D.shape[2])
        axs[i].set_ylim(0, arr3D.shape[1])
        axs[i].set_box_aspect(1)
        # axs[i].xaxis.set_major_locator(loc)
        # axs[i].yaxis.set_major_locator(loc)
        i = 1
        axs[i].set_xlabel("y(pt)",fontsize = labelFontSize)
        axs[i].set_ylabel("z(pt)",fontsize = labelFontSize, rotation=0)
        axs[i].xaxis.set_label_coords(1.0, -0.1)  # Adjust corresponding label coordinates relative to the axes
        axs[i].yaxis.set_label_coords(-0.15, 1.05)  # Adjust corresponding label coordinates relative to the axes
        axs[i].tick_params(axis='both', which='major', labelsize=tickFontSize)
        axs[i].set_xlim(0, arr3D.shape[1])
        axs[i].set_ylim(0, arr3D.shape[0])
        axs[i].set_box_aspect(1)
        # axs[i].xaxis.set_major_locator(loc)
        # axs[i].yaxis.set_major_locator(loc)
        i = 2
        axs[i].set_xlabel("x(pt)",fontsize = labelFontSize)
        axs[i].set_ylabel("z(pt)",fontsize = labelFontSize, rotation=0)
        axs[i].xaxis.set_label_coords(1.0, -0.1)  # Adjust corresponding label coordinates relative to the axes
        axs[i].yaxis.set_label_coords(-0.15, 1.05)  # Adjust corresponding label coordinates relative to the axes
        axs[i].tick_params(axis='both', which='major', labelsize=tickFontSize)
        axs[i].set_xlim(0, arr3D.shape[2])
        axs[i].set_ylim(0, arr3D.shape[0])
        axs[i].set_box_aspect(1)
        # axs[i].xaxis.set_major_locator(loc)
        # axs[i].yaxis.set_major_locator(loc)

        axs[0].pcolormesh(arr3D[arr3D.shape[0] // 2, :, :], cmap=cmap, vmin=0, vmax=maxIntensity)
        axs[1].pcolormesh(arr3D[:, arr3D.shape[1] // 2, :], cmap=cmap, vmin=0, vmax=maxIntensity)
        axs[2].pcolormesh(arr3D[:, :, arr3D.shape[2] // 2], cmap=cmap, vmin=0, vmax=maxIntensity)
        cbar = plt.colorbar(axs[2].collections[0], ax=axs[2], orientation='horizontal')
        
        cbar.ax.tick_params(labelsize=tickFontSize)
        cbar.set_label('Intensity', fontsize=labelFontSize)  # Set the colorbar label and font size
        # plt.subplots_adjust(hspace=0.0)
        # plt.show()
        return fig

    @staticmethod
    def FigureToImage(fig:plt.Figure)-> Image:
        """
        Convert a Matplotlib figure object into a PIL Image object.
        Args:
            fig (matplotlib.figure.Figure): The figure to convert.
        Returns:
            PIL.Image.Image: The converted image.
        """
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img = Image.open(buf)
        return img

    def FigurePILImagekFrom3DArray(arr3D: np.ndarray, plotName:str=None, widthPt=300, heightPt = 900, dpiIn = 300)->Image:
        """Function create PIL.Image  object of figure with 3 slices of 3D array using matplotlib.
        
        Input: arr3d - 3d ndarray
               plotName - plot header name.
        Returns:
                PIL.Image object
        """
        fig = AuxCanvasPlot.FigureFrom3DArray(arr3D = arr3D,  plotName=plotName, widthPt=widthPt, heightPt = heightPt, dpiIn = dpiIn)
        return AuxCanvasPlot.FigureToImage(fig)
