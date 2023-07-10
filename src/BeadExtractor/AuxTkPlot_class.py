import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as plticker
import matplotlib.cm as cm
from tkinter import Canvas
import itertools

class AuxCanvasPlot():
    def FigureCanvasTkFrom3DArray(arr3D: np.ndarray, cnv:Canvas, plotName="Plot"):
        """Function create FigureCanvasTk  object of figure with 3 slices of 3D array.
        this object can be used to get widget for Tkinter object.get_tk_widget()
        Input: arr3d - 3d ndarray
                cnv - canvas
                plotName - plot header name. if plotName= " " then no plotName.
        Returns:
                FigureCanvasTk  object
                hint: use FigureCanvasTk.get_tk_widget().pack/grid() after to plot
        """
        # creating figure with matplotlib
        fig, axs = plt.subplots(nrows=3, sharex=False, figsize=(2, 6), layout="constrained")
        if plotName != " ":
            fig.suptitle(plotName)
        cmap = cm.jet
        loc = plticker.MultipleLocator(base=10.0)  # ticks step setup

        i = 0
        # axs[i].set_title("X-Y")
        axs[i].set_xlabel("x")
        axs[i].set_ylabel("y")
        axs[i].set_xlim(0, arr3D.shape[2])
        axs[i].set_ylim(0, arr3D.shape[1])
        axs[i].set_box_aspect(1)
        axs[i].xaxis.set_major_locator(loc)
        axs[i].yaxis.set_major_locator(loc)
        i = 1
        axs[i].set_xlabel("y")
        axs[i].set_ylabel("z")
        axs[i].set_xlim(0, arr3D.shape[1])
        axs[i].set_ylim(0, arr3D.shape[0])
        axs[i].set_box_aspect(1)
        axs[i].xaxis.set_major_locator(loc)
        axs[i].yaxis.set_major_locator(loc)
        i = 2
        axs[i].set_xlabel("x")
        axs[i].set_ylabel("z")
        axs[i].set_xlim(0, arr3D.shape[2])
        axs[i].set_ylim(0, arr3D.shape[0])
        axs[i].set_box_aspect(1)
        axs[i].xaxis.set_major_locator(loc)
        axs[i].yaxis.set_major_locator(loc)

        axs[0].pcolormesh(arr3D[arr3D.shape[0] // 2, :, :], cmap=cmap)
        axs[1].pcolormesh(arr3D[:, arr3D.shape[1] // 2, :], cmap=cmap)
        axs[2].pcolormesh(arr3D[:, :, arr3D.shape[2] // 2], cmap=cmap)
        # plt.show()
        # Instead of plt.show creating Tkwidget from figure on the canvas self.cnvImg
        return FigureCanvasTkAgg(fig, cnv)


    def FigureCanvasTk3DFrom3DArray(arr3D: np.ndarray, cnv:Canvas, treshold=np.exp(-1) * 255.0):
        """Function create FigureCanvasTk  object 3D view of a given  3D array.
        this object can be used to get widget for Tkinter object.get_tk_widget()
        Input: arr3d - 3d ndarray
                cnv - canvas
                plotName - plot header name. if plotName= " " then no plotName.
        Returns:
                FigureCanvasTk  object
                hint: use FigureCanvasTk.get_tk_widget().pack/grid() after to plot
        """ 
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
