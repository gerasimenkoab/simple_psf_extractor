import numpy as np
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from PIL import ImageTk, Image, ImageEnhance
from .AuxTkPlot_class import AuxCanvasPlot

"""   TODO:
        - fix  AuxTkPlot_class  for all modules
       - add  bead size to tiff tag
"""


class DeconImageView(tk.Toplevel):
    """GUI class"""

    def __init__(self, parent, wwidth=600, wheight=600):
        super().__init__(parent)
        pass