import numpy as np
import io
import tkinter as tk
from tkinter import Canvas
from PIL import Image
from PIL import ImageTk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as plticker
import matplotlib.cm as cm
from matplotlib.colors import Normalize
import matplotlib.colors as colors
import itertools


class AuxCanvasPlot():
    """Class for creation image for tkinter with matplotlib and PIL """

    def Draw2DArrayOnCanvasPIL(arrayIn, canvas: Canvas):
         # need to call widget.update to get correct values for winfo_width/height
        canvas.update()
        height = canvas.winfo_height()
        width = canvas.winfo_width()
        imagePIL = Image.fromarray(arrayIn)
        # bound ImageTk to out widget - cnv, so set cnv.image. It is done to prevent GC to remove image.                               
        canvas.image = ImageTk.PhotoImage(image = imagePIL.resize((width, height)))
        # replacing image on the canvas
        canvas.create_image((0, 0), image=canvas.image, state = 'normal', anchor=tk.NW)

    def FigureCanvasTkFrom2DArray(arr2D: np.ndarray, cnv:Canvas, plotName=""):
        """Function create FigureCanvasTk widget  object of 2D array using matplotlib.
        this object can be used to get widget for Tkinter object.get_tk_widget()
        Input: arr2d - 2d ndarray
                cnv - canvas
                plotName - plot header name. if plotName= " " then no plotName.
        Returns:
                FigureCanvasTk widget  object
                hint: use .pack/grid() after to plot
        """
        if arr2D.ndim != 2:
            raise ValueError("Not a 2D array recieved.", "wrong-array-dimensions")
        fig, ax = plt.subplots(1, 1, sharex=False, figsize=(1, 1))
        if plotName != "":
            fig.suptitle(plotName)
        dN = arr2D.shape[0]
        ax.pcolormesh(arr2D, cmap=cm.jet)
        return FigureCanvasTkAgg(fig, cnv)#.get_tk_widget()
        # .pack( side=TOP, fill=BOTH, expand=True )

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
        heightInch = heightPt * 1.05 / dpiSet
        # widthInch = 1.5
        # heightInch = 4.5
        # creating figure with matplotlib
        fig, axs = plt.subplots(nrows=3, sharex=False, figsize=(widthInch, heightInch),dpi = dpiSet, layout="constrained")
        
        #fig.subplots_adjust(left=0.01, right=0.1)  # Adjust subplot position not compatible with  layout="constrained"
        if plotName is not None:
           fig.suptitle(plotName)
        loc = plticker.MultipleLocator(base=10.0)  # ticks step setup
        labelFontSize = int(dpiIn /50)
        tickFontSize = labelFontSize -1
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
    
    def FigureCanvasTkFrom3DArray(arr3D: np.ndarray, cnv:Canvas, plotName:str=None, widthPt=100, heightPt = 300, dpiIn = 100):
        """Function create FigureCanvasTk  object of figure with 3 slices of 3D array using matplotlib.
        this object can be used to get widget for Tkinter object.get_tk_widget()
        Input: arr3d - 3d ndarray
                cnv - canvas
                plotName - plot header name. if plotName= " " then no plotName.
        Returns:
                FigureCanvasTk  object
                hint: use FigureCanvasTk.get_tk_widget().pack/grid() after to plot
        """
        fig = AuxCanvasPlot.FigureFrom3DArray(arr3D = arr3D, plotName=plotName, widthPt=widthPt, heightPt = heightPt, dpiIn = dpiIn)
        return FigureCanvasTkAgg(fig, cnv)
    
    @staticmethod
    def FigureToImage(fig:plt.Figure)->Image:
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

    def FigurePILImagekFrom3DArray(arr3D: np.ndarray, plotName:str=None, widthPt=100, heightPt = 300, dpiIn = 100)->Image:
        """Function create PIL.Image  object of figure with 3 slices of 3D array using matplotlib.
        
        Input: arr3d - 3d ndarray
               plotName - plot header name.
        Returns:
                PIL.Image object
        """
        fig = AuxCanvasPlot.FigureFrom3DArray(arr3D = arr3D,  plotName=plotName, widthPt=widthPt, heightPt = heightPt, dpiIn = dpiIn)
        return AuxCanvasPlot.FigureToImage(fig)
    
    def FigureCanvasTk3DFrom3DArray(arr3D: np.ndarray, cnv:Canvas, treshold=np.exp(-1) * 255.0):
        """Function create FigureCanvasTk  object 3D view of a given  3D array  using matplotlib.
        this object can be used to get widget for Tkinter object.get_tk_widget()
        Input: arr3d - 3d ndarray
                cnv - canvas
                plotName - plot header name. if plotName= " " then no plotName.
        Returns:
                FigureCanvasTk  object
                hint: use FigureCanvasTk.get_tk_widget().pack/grid() after to plot
        """ 
        if arr3D.ndim != 3:
            raise ValueError("Not a 3D array recieved.", "wrong-array-dimensions")
        # теперь разбрасываем бид по отдельным массивам .
        zcoord = np.zeros(arr3D.shape[0] * arr3D.shape[1] * arr3D.shape[2])
        xcoord = np.zeros(arr3D.shape[0] * arr3D.shape[1] * arr3D.shape[2])
        ycoord = np.zeros(arr3D.shape[0] * arr3D.shape[1] * arr3D.shape[2])
        voxelVal = np.zeros(arr3D.shape[0] * arr3D.shape[1] * arr3D.shape[2])
        nn = 0
        arr3D = arr3D / np.amax(arr3D) * 255.0
        for i, j, k in itertools.product(
            range(arr3D.shape[0]), range(arr3D.shape[1]), range(arr3D.shape[2])
        ):
            zcoord[nn] = i
            xcoord[nn] = j
            ycoord[nn] = k
            voxelVal[nn] = arr3D[i, j, k]
            nn = nn + 1
        fig1 = plt.figure()
        ax = fig1.add_subplot(111, projection="3d")
        selection = voxelVal > treshold
        im = ax.scatter(
            xcoord[selection],
            ycoord[selection],
            zcoord[selection],
            c=voxelVal[selection],
            alpha=0.5,
            cmap=cm.jet,
        )
        fig1.colorbar(im)
        ax.set_zlabel("Z")
        ax.set_ylabel("Y")
        ax.set_xlabel("X")
        return FigureCanvasTkAgg(fig1, cnv)
