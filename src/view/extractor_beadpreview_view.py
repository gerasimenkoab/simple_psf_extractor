import numpy as np
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showerror
from PIL import ImageTk, Image, ImageEnhance

try:
    from .AuxTkPlot_class import AuxCanvasPlot
except:
    from AuxTkPlot_class import AuxCanvasPlot

"""   TODO:
        - colored Preview
        - line graph Preview
"""



class ExtractorBeadPreviewWidget(tk.Toplevel):
    def __init__(self, master=None, **kw):
        super(ExtractorBeadPreviewWidget, self).__init__(master, **kw)
        self.mainFrame = ttk.Frame(self)
        self.mainFrame.configure(height=600, width=600)
        self.colorPlotframe = ttk.Frame(self.mainFrame)
        self.colorPlotframe.configure(height=480, width=210)
        self.colotPlotXY = tk.Canvas(self.colorPlotframe)
        self.colotPlotXY.configure(height=150, width=150)
        self.colotPlotXY.pack(
            expand=True,
            fill="both",
            padx=2,
            pady=2,
            side="top")
        self.colorPlotXZ = tk.Canvas(self.colorPlotframe)
        self.colorPlotXZ.configure(height=150, width=150)
        self.colorPlotXZ.pack(
            expand=True,
            fill="both",
            padx=2,
            pady=2,
            side="top")
        self.colorPlotYZ = tk.Canvas(self.colorPlotframe)
        self.colorPlotYZ.configure(height=150, width=150)
        self.colorPlotYZ.pack(
            expand=True,
            fill="both",
            padx=2,
            pady=2,
            side="top")
        self.colorPlotframe.grid(
            column=0, padx=2, pady=5, row=0, sticky="nsew")
        separator1 = ttk.Separator(self.mainFrame)
        separator1.configure(orient="vertical")
        separator1.grid(column=1, padx=2, pady=5, row=0, sticky="ns")
        self.linePlotFrame = ttk.Frame(self.mainFrame)
        self.linePlotFrame.configure(height=480, width=210)
        self.linePlotXY = tk.Canvas(self.linePlotFrame)
        self.linePlotXY.configure(height=150, width=150)
        self.linePlotXY.pack(
            expand=True,
            fill="both",
            padx=2,
            pady=2,
            side="top")
        self.linePlotXZ = tk.Canvas(self.linePlotFrame)
        self.linePlotXZ.configure(height=150, width=150)
        self.linePlotXZ.pack(
            expand=True,
            fill="both",
            padx=2,
            pady=2,
            side="top")
        self.linePlotYZ = tk.Canvas(self.linePlotFrame)
        self.linePlotYZ.configure(height=150, width=150)
        self.linePlotYZ.pack(
            expand=True,
            fill="both",
            padx=2,
            pady=2,
            side="top")
        self.linePlotFrame.grid(column=2, padx=2, pady=5, row=0, sticky="nsew")
        separator2 = ttk.Separator(self.mainFrame)
        separator2.configure(orient="vertical")
        separator2.grid(column=3, padx=2, pady=5, row=0, sticky="ns")
        self.controlFrame = ttk.Frame(self.mainFrame)
        self.controlFrame.configure(height=480, width=210)
        self.controlsLabel = tk.Label(self.controlFrame)
        self.controlsLabel.configure(padx=55, text='Selected Beads')
        self.controlsLabel.pack(padx=2, pady=2, side="top")
        self.beadListFrame = ttk.Frame(self.controlFrame)
        self.beadListFrame.configure(height=200, width=200)
        self.beadsList = tk.Listbox(self.beadListFrame)
        self.beadsList.grid(column=0, row=0, sticky="nsew")
        self.beadsList.configure(yscrollcommand=self.beadListscroll)
        self.beadListScroll = ttk.Scrollbar(self.beadListFrame)
        self.beadListScroll.configure(orient="vertical")
        self.beadListScroll.grid(column=1, row=0, sticky="ns")
        self.beadListScroll.configure(command=self.beadList)
        self.beadListFrame.pack(
            expand=True,
            fill="both",
            padx=2,
            pady=2,
            side="top")
        self.beadListFrame.rowconfigure(0, weight=1)
        self.beadListFrame.columnconfigure(0, weight=1)
        self.deleteBeadBtn = ttk.Button(self.controlFrame)
        self.deleteBeadBtn.configure(text='Delete', underline=0)
        self.deleteBeadBtn.pack(fill="x", padx=2, pady=2, side="top")
        self.preview2DBtn = ttk.Button(self.controlFrame)
        self.preview2DBtn.configure(text='Preview 2D')
        self.preview2DBtn.pack(fill="x", padx=2, pady=2, side="top")
        self.preview3DBtn = ttk.Button(self.controlFrame)
        self.preview3DBtn.configure(text='Preview 3D')
        self.preview3DBtn.pack(fill="x", padx=2, pady=2, side="top")
        self.controlFrame.grid(column=4, padx=2, pady=5, row=0, sticky="ns")
        self.mainFrame.pack(expand=True, fill="both", side="top")
        self.mainFrame.rowconfigure(0, weight=10)
        self.mainFrame.columnconfigure(0, weight=2)
        self.mainFrame.columnconfigure(2, weight=2)
        self.configure(height=200, width=200)
        self.geometry("640x480")
        self.minsize(640, 480)

    def beadListscroll(self, first, last):
        pass

    def beadList(self, mode=None, value=None, units=None):
        pass



if __name__ == "__main__":
    root = tk.Tk()
    widget = ExtractorBeadPreviewWidget(root)
    # widget.pack(expand=True, fill="both")
    root.mainloop()
