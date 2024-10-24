import numpy as np
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showerror
from PIL import ImageTk, Image, ImageEnhance
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.cm as cm


try:
    from ..common.AuxTkPlot_class import AuxCanvasPlot
except:
    from common.AuxTkPlot_class import AuxCanvasPlot

"""   TODO:
        - colored Preview
        - line graph Preview
"""


class ExtractorBeadPreviewWidget(tk.Toplevel):
    def __init__(self, master=None, **kw):
        super(ExtractorBeadPreviewWidget, self).__init__(master, **kw)
        self.title("Bead Preview")
        self.mainFrame = ttk.Frame(self)
        self.mainFrame.configure(height=600, width=600)
        self.colorPlotframe = ttk.Frame(self.mainFrame)
        self.colorPlotframe.configure(height=480, width=210)
        # ----------------------------- Colormech Plots----------------------------------------
        self.colorPlotXY, self.axisXY = self.create_canvas(
            self.colorPlotframe, 1.5, 1.5, 100
        )
        self.colorPlotXY.get_tk_widget().pack(
            expand=True, fill="both", padx=2, pady=2, side="top"
        )
        self.colorPlotXY.draw()

        self.colorPlotXZ, self.axisXZ = self.create_canvas(
            self.colorPlotframe, 1.5, 1.5, 100
        )
        self.colorPlotXZ.get_tk_widget().pack(
            expand=True, fill="both", padx=2, pady=2, side="top"
        )
        self.colorPlotXZ.draw()

        self.colorPlotYZ, self.axisYZ = self.create_canvas(
            self.colorPlotframe, 1.5, 1.5, 100
        )
        self.colorPlotYZ.get_tk_widget().pack(
            expand=True, fill="both", padx=2, pady=2, side="top"
        )
        self.colorPlotYZ.draw()

        self.colorPlotframe.grid(column=0, padx=2, pady=5, row=0, sticky="nsew")
        separator1 = ttk.Separator(self.mainFrame)
        separator1.configure(orient="vertical")
        separator1.grid(column=1, padx=2, pady=5, row=0, sticky="ns")
        # ------------------------------------------- Line Plots ------------------------------
        self.linePlotFrame = ttk.Frame(self.mainFrame)
        self.linePlotFrame.configure(height=480, width=210)

        self.linePlotXY, self.axisLXY = self.create_canvas(
            self.linePlotFrame, 1.5, 1.5, 100
        )
        self.linePlotXY.get_tk_widget().pack(
            expand=True, fill="both", padx=2, pady=2, side="top"
        )
        self.linePlotXY.draw()

        self.linePlotXZ, self.axisLXZ = self.create_canvas(
            self.linePlotFrame, 1.5, 1.5, 100
        )
        self.linePlotXZ.get_tk_widget().pack(
            expand=True, fill="both", padx=2, pady=2, side="top"
        )
        self.linePlotXZ.draw()

        self.linePlotYZ, self.axisLYZ = self.create_canvas(
            self.linePlotFrame, 1.5, 1.5, 100
        )
        self.linePlotYZ.get_tk_widget().pack(
            expand=True, fill="both", padx=2, pady=2, side="top"
        )
        self.linePlotYZ.draw()

        self.linePlotFrame.grid(column=2, padx=2, pady=5, row=0, sticky="nsew")
        separator2 = ttk.Separator(self.mainFrame)
        separator2.configure(orient="vertical")
        separator2.grid(column=3, padx=2, pady=5, row=0, sticky="ns")
        # ------------------------------------- Controls Frame --------------------------------------
        self.controlFrame = ttk.Frame(self.mainFrame)
        self.controlFrame.configure(height=480, width=210)
        self.controlsLabel = tk.Label(self.controlFrame)
        self.controlsLabel.configure(padx=55, text="Selected Beads")
        self.controlsLabel.pack(padx=2, pady=2, side="top")

        self.beadListFrame = ttk.Frame(self.controlFrame)
        self.beadListFrame.configure(height=200, width=200)
        self.beadsList = tk.Listbox(self.beadListFrame)
        self.beadsList.grid(column=0, row=0, sticky="nsew")
        self.beadListScroll = ttk.Scrollbar(
            self.beadListFrame, orient=tk.VERTICAL, command=self.beadsList.yview
        )
        self.beadsList.configure(yscrollcommand=self.beadListScroll)
        self.beadListScroll.grid(column=1, row=0, sticky="ns")
        self.beadListFrame.pack(expand=True, fill="both", padx=2, pady=2, side="top")
        self.beadListFrame.rowconfigure(0, weight=1)
        self.beadListFrame.columnconfigure(0, weight=1)

        self.deleteBeadBtn = ttk.Button(self.controlFrame)
        self.deleteBeadBtn.configure(text="Delete", underline=0)
        self.deleteBeadBtn.pack(fill="x", padx=2, pady=2, side="top")

        self.preview3DBtn = ttk.Button(self.controlFrame)
        self.preview3DBtn.configure(text="Preview 3D")
        self.preview3DBtn.pack(fill="x", padx=2, pady=2, side="top")

        self.previewCloseBtn = ttk.Button(self.controlFrame)
        self.previewCloseBtn.configure(text="Close")
        self.previewCloseBtn.pack(fill="x", padx=2, pady=2, side="top")
        self.previewCloseBtn.config(command=self.CloseBeadPreview)
        self.controlFrame.grid(column=4, padx=2, pady=5, row=0, sticky="ns")
        self.mainFrame.pack(expand=True, fill="both", side="top")
        self.mainFrame.rowconfigure(0, weight=10)
        self.mainFrame.columnconfigure(0, weight=2)
        self.mainFrame.columnconfigure(2, weight=2)
        self.configure(height=200, width=200)
        self.geometry("640x480")
        self.minsize(640, 480)
        # bring widget in the center of the screen area
        self.update_idletasks()
        self.lift()


    def SetBeadList(self, beadCoords = None):
        """ Load beads list form controller """
        if beadCoords is None:
            showerror("Caution", "Bead list is empty!")
            return
        self.beadsList.delete(0, tk.END)
        self._beadCoords = beadCoords
        self.beadsList.insert(0, *self._beadCoords)
        self.beadsList.selection_set(0)

    def beadListViewGet(self):
        return self.beadsList.curselection()[0]

    def PlotBeadPreview2D(self, arrayIn = None):
        if arrayIn is None:
            self.ClearPlots()
            return
        centerX = arrayIn.shape[2] // 2 
        centerY = arrayIn.shape[1] // 2
        centerZ = arrayIn.shape[0] // 2
        arrXY = arrayIn[centerZ,:,:].reshape((arrayIn.shape[1],arrayIn.shape[2]))
        arrXZ = arrayIn[:,centerY,:].reshape((arrayIn.shape[0],arrayIn.shape[2]))
        arrYZ = arrayIn[:,:,centerX].reshape((arrayIn.shape[0],arrayIn.shape[1]))
        y1 = arrayIn[centerZ,centerY,:].reshape((arrayIn.shape[2]))
        x1 = range(len(y1))
        y2 = arrayIn[centerZ,:,centerX].reshape((arrayIn.shape[1]))
        x2 = range(len(y2))
        y3 = arrayIn[:,centerY,centerX].reshape((arrayIn.shape[0]))
        x3 = range(len(y3))

        self.plotNumpyArrayColormesh2D(
            self.axisXY, self.colorPlotXY, arrXY, xlabel="X(px)", ylabel="Y(px)"
        )
        self.plotNumpyArrayColormesh2D(
            self.axisXZ, self.colorPlotXZ, arrXZ, xlabel="X(px)", ylabel="Z(px)"
        )
        self.plotNumpyArrayColormesh2D(
            self.axisYZ, self.colorPlotYZ, arrYZ, xlabel="Y(px)", ylabel="Z(px)"
        )
        self.plotArrayLine(
            self.axisLXY, self.linePlotXY, x1, y1, xlabel="n(px)", ylabel="Intensity X"
        )
        self.plotArrayLine(
            self.axisLXZ, self.linePlotXZ, x2, y2, xlabel="n(px)", ylabel="Intensity Y"
        )
        self.plotArrayLine(
            self.axisLYZ, self.linePlotYZ, x3, y3, xlabel="n(px)", ylabel="Intensity Z"
        )

    def ClearPlots(self):
        self.axisXY.clear()
        self.axisXZ.clear()
        self.axisYZ.clear()
        self.axisLXY.clear()
        self.axisLXZ.clear()
        self.axisLYZ.clear()
        self.colorPlotXY.draw()
        self.colorPlotXZ.draw()
        self.colorPlotYZ.draw()
        self.linePlotXY.draw()
        self.linePlotXZ.draw()
        self.linePlotYZ.draw()

    def PlotBeadPreview3D(self, beadArray, winTitle="3D Plot"):
        """ Plots three bead in 3D pointplot"""
        try:
            # popup window creation with canvas and exit button
            child_tmp = tk.Toplevel(self)
            child_tmp.title(winTitle)
            cnvPlot = tk.Canvas(child_tmp, width=300, height=300)
            cnvPlot.pack(side="top")
            ttk.Button(child_tmp, text="Close", command=child_tmp.destroy).pack(
                side="top"
            )

            AuxCanvasPlot.FigureCanvasTk3DFrom3DArray(
                beadArray, cnvPlot
            ).get_tk_widget().pack(side="top")
        except Exception as e:
            raise RuntimeError("Bead 3D plot failed. " + str(e))

    def create_canvas(self, masterFrame, height=1.5, width=1.5, dpi=100):
        # Create a canvas to hold the matplotlib figure
        fig = Figure(figsize=(width, height), dpi=dpi, layout="constrained")
        fig.patch.set_facecolor("grey")  # setting up puter background
        fig.patch.set_alpha(0.1)
        ax = fig.add_subplot(111)
        ax.set_xlabel("x(pt)", fontsize=8)
        ax.set_ylabel("y(pt)", fontsize=8)
        ax.tick_params(axis="both", which="major", labelsize=8)
        # ax.set_box_aspect(1)
        canvas = FigureCanvasTkAgg(fig, master=masterFrame)
        return canvas, ax

    def plotArrayLine(self, ax, canvas, x, y, xlabel="X-axis", ylabel="Y-axis"):
        # Plot the line on the existing canvas
        ax.clear()
        ax.plot(x, y)
        ax.set_xlim(0, y.shape[0])
        ax.set_ylim(0, np.max(y))
        ax.set_xlabel(xlabel, fontsize=8)
        ax.set_ylabel(ylabel, fontsize=8)
        ax.legend()
        canvas.draw()

    def plotNumpyArrayColormesh2D(
        self, ax, canvas, data, xlabel="X-axis", ylabel="Y-axis"
    ):
        # Plot the data on the existing canvas
        ax.clear()
        ax.set_xlim(0, data.shape[1])
        ax.set_ylim(0, data.shape[0])
        ax.set_xlabel(xlabel, fontsize=8)
        ax.set_ylabel(ylabel, fontsize=8)
        im = ax.imshow(data, cmap=cm.jet)
        canvas.draw()

    def CloseBeadPreview(self, event=None):
        """Default close window method """
        self.destroy()



if __name__ == "__main__":
    root = tk.Tk()
    root.title("Bead Preview Test")
    root.geometry("300x30")
    # close window button at root window
    closeButton = ttk.Button(root, text="Close", command=root.destroy)
    closeButton.pack()
    widget = ExtractorBeadPreviewWidget(root)
    # widget.PlotColorGraphs()
    # widget.pack(expand=True, fill="both")
    root.mainloop()
