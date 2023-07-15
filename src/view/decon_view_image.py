import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image, ImageEnhance
#from .AuxTkPlot_class import AuxCanvasPlot

"""   TODO:
        - fix  AuxTkPlot_class  for all modules
       - add  bead size to tiff tag
"""


class deconImageFrameNb(tk.Frame):
        """
        Frame for deconView Notebook page dedicated to PSF deconvolution
        """
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # self = ttk.Frame( master )
            # self.configure(height=200, width=200)
            self.deconImage_settings = ttk.Frame(self)
            self.deconImage_settings.configure(height=200, width=200)

            self.step1Image_frm = ttk.Frame(self.deconImage_settings)
            self.step1Image_frm.configure(height=200, width=200)
            self.step1Image_lbl = ttk.Label(self.step1Image_frm)
            self.step1Image_lbl.configure(font="TkCaptionFont", text='Load Image')
            self.step1Image_lbl.pack(pady=10, side="top")

            self.step1Image_load_frm = ttk.Frame(self.step1Image_frm)
            self.step1Image_load_frm.configure(height=200, width=200)
            self.loadImage_btn = ttk.Button(self.step1Image_load_frm)
            self.loadImage_btn.configure(text='Load Image')
            self.loadImage_btn.pack(padx=5, side="left")
            entryImage = ttk.Entry(self.step1Image_load_frm)
            entryImage.configure(state="readonly")
            _text_ = 'No Image Loaded'
            entryImage["state"] = "normal"
            entryImage.delete("0", "end")
            entryImage.insert("0", _text_)
            entryImage["state"] = "readonly"
            entryImage.pack(expand=True, fill="x", padx=5, pady=5, side="right")
            self.step1Image_load_frm.pack(expand=True, fill="both", padx=5, side="top")
            #
            self.step1psf_lbl = ttk.Label(self.step1Image_frm)
            self.step1psf_lbl.configure(font="TkCaptionFont", text='Load PSF')
            self.step1psf_lbl.pack(pady=10, side="top")

            self.step1psf_load_frm = ttk.Frame(self.step1Image_frm)
            self.step1psf_load_frm.configure(height=200, width=200)
            self.loadPSF_btn = ttk.Button(self.step1psf_load_frm)
            self.loadPSF_btn.configure(text='Load PSF')
            self.loadPSF_btn.pack(padx=5, side="left")
            entryPSF = ttk.Entry(self.step1psf_load_frm)
            entryPSF.configure(state="readonly")
            _text_ = 'No Image Loaded'
            entryPSF["state"] = "normal"
            entryPSF.delete("0", "end")
            entryPSF.insert("0", _text_)
            entryPSF["state"] = "readonly"
            entryPSF.pack(expand=True, fill="x", padx=5, pady=5, side="right")
            self.step1psf_load_frm.pack(expand=True, fill="both", padx=5, side="top")
#
            self.step1psf_sep = ttk.Separator(self.step1Image_frm)
            self.step1psf_sep.configure(orient="horizontal")
            self.step1psf_sep.pack(
                expand=True,
                fill="x",
                padx=10,
                pady=10,
                side="top")
            self.step1Image_frm.pack(expand=True, fill="both", side="top")
            self.deconImage_settings.pack(expand=True, fill="both", side="left")

            self.pack(expand=True, fill="both", side="top")
