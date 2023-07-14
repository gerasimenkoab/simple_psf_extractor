import numpy as np
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from PIL import ImageTk, Image, ImageEnhance
#from .AuxTkPlot_class import AuxCanvasPlot

"""   TODO:
        - fix  AuxTkPlot_class  for all modules
       - add  bead size to tiff tag
"""


class DeconPsfView:
    def __init__(self, master=None):
        # build ui
#        self.logger = logging.getLogger('__main__.'+__name__)
#        self.logger.info("Decon PSF view loaded")

        self.deconPsfToplevel = tk.Tk() if master is None else tk.Toplevel(master)
        self.deconPsfToplevel.configure(
            height=768,
            padx=5,
            pady=5,
            takefocus=True,
            width=1024)
        self.deconPsfToplevel.geometry("1024x768")
        self.deconPsfToplevel.maxsize(1920, 1080)
        self.deconPsfToplevel.minsize(1024, 768)
        self.deconPsfToplevel.resizable(True, True)
        self.deconPsfToplevel.title("Deconvolution widget")

        self.deconNotebook = ttk.Notebook(self.deconPsfToplevel)
        self.deconNotebook.configure(height=200, width=200)
        self.deconNotebook.pack(expand=True, fill="both", side="top")

        self.deconPsfFrame = ttk.Frame(self.deconNotebook)
        self.deconPsfFrame.configure(height=200, width=200)
        self.deconPSF_settings = ttk.Frame(self.deconPsfFrame)
        self.deconPSF_settings.configure(height=200, width=200)
        self.step1_frm = ttk.Frame(self.deconPSF_settings)
        self.step1_frm.configure(height=200, width=200)
        self.step1_lbl = ttk.Label(self.step1_frm)
        self.step1_lbl.configure(font="TkCaptionFont", text='Load Bead Image')
        self.step1_lbl.pack(pady=10, side="top")
        self.step1_load_frm = ttk.Frame(self.step1_frm)
        self.step1_load_frm.configure(height=200, width=200)
        self.loadPSF_btn = ttk.Button(self.step1_load_frm)
        self.loadPSF_btn.configure(text='Load Image')
        self.loadPSF_btn.pack(padx=5, side="left")
        entry4 = ttk.Entry(self.step1_load_frm)
        entry4.configure(state="readonly")
        _text_ = 'No Image Loaded'
        entry4["state"] = "normal"
        entry4.delete("0", "end")
        entry4.insert("0", _text_)
        entry4["state"] = "readonly"
        entry4.pack(expand=True, fill="x", padx=5, pady=5, side="right")
        self.step1_load_frm.pack(expand=True, fill="both", padx=5, side="top")
        self.step1_sep = ttk.Separator(self.step1_frm)
        self.step1_sep.configure(orient="horizontal")
        self.step1_sep.pack(
            expand=True,
            fill="x",
            padx=10,
            pady=10,
            side="top")
        self.step1_frm.pack(expand=True, fill="both", side="top")
        self.step2 = ttk.Frame(self.deconPSF_settings)
        self.step2.configure(height=200, width=200)
        self.step2_lbl = ttk.Label(self.step2)
        self.step2_lbl.configure(text='Bead Parameters')
        self.step2_lbl.pack(side="top")
        frame16 = ttk.Frame(self.step2)
        frame16.configure(height=200, width=200)
        frame17 = ttk.Frame(frame16)
        frame17.configure(height=200, width=200)
        self.beadSize_lbl = ttk.Label(frame17)
        self.beadSize_lbl.configure(text='Bead Size (nm):')
        self.beadSize_lbl.pack(padx=5, pady=5, side="left")
        self.beadSize_entry = ttk.Entry(frame17)
        self.beadSize_entry.configure(validate="focusout", width=10)
        self.beadSize_entry.pack(padx=5, pady=5, side="left")
        frame17.pack(side="top")
        frame18 = ttk.Frame(frame16)
        frame18.configure(height=200, width=200)
        label8 = ttk.Label(frame18)
        label8.configure(text='Voxel')
        label8.pack(padx=2, pady=2, side="left")
        label11 = ttk.Label(frame18)
        label11.configure(text='X:')
        label11.pack(padx=2, pady=2, side="left")
        entry6 = ttk.Entry(frame18)
        entry6.configure(state="normal", validate="focusout", width=5)
        entry6.pack(padx=5, pady=5, side="left")
        label9 = ttk.Label(frame18)
        label9.configure(text='Y:')
        label9.pack(padx=2, pady=2, side="left")
        entry7 = ttk.Entry(frame18)
        entry7.configure(state="normal", validate="focusout", width=5)
        entry7.pack(padx=2, pady=2, side="left")
        label10 = ttk.Label(frame18)
        label10.configure(text='Z:')
        label10.pack(padx=2, pady=2, side="left")
        entry8 = ttk.Entry(frame18)
        entry8.configure(state="normal", validate="focusout", width=5)
        entry8.pack(padx=2, pady=2, side="left")
        frame18.pack(side="top")
        frame16.pack(expand=True, fill="both", side="top")
        separator3 = ttk.Separator(self.step2)
        separator3.configure(orient="horizontal")
        separator3.pack(fill="x", padx=10, pady=10, side="top")
        self.step2.pack(expand=True, fill="both", padx=5, pady=5, side="top")
        self.step3 = ttk.Frame(self.deconPSF_settings)
        self.step3.configure(height=200, width=200)
        label12 = ttk.Label(self.step3)
        label12.configure(text='Deconvolution parameters')
        label12.pack(side="top")
        frame24 = ttk.Frame(self.step3)
        frame24.configure(height=200, width=200)
        label17 = ttk.Label(frame24)
        label17.configure(text='Method:')
        label17.pack(padx=2, pady=5, side="left")
        combobox2 = ttk.Combobox(frame24)
        self.deconMethodMenuStrVal = tk.StringVar()
        combobox2.configure(textvariable=self.deconMethodMenuStrVal)
        combobox2.pack(padx=2, pady=5, side="left")
        frame24.pack(side="top")
        frame20 = ttk.Frame(self.step3)
        frame20.configure(height=200, width=200)
        progressbar1 = ttk.Progressbar(frame20)
        progressbar1.configure(orient="horizontal")
        progressbar1.pack(padx=2, pady=5, side="top")
        self.calc = ttk.Button(frame20)
        self.calc.configure(text='Calculate PSF')
        self.calc.pack(padx=2, pady=5, side="top")
        frame20.pack(side="top")
        frame22 = ttk.Frame(self.step3)
        frame22.configure(height=200, width=200)
        label14 = ttk.Label(frame22)
        label14.configure(text='Iteration number:')
        label14.pack(padx=2, pady=5, side="left")
        entry9 = ttk.Entry(frame22)
        entry9.configure(width=10)
        entry9.pack(padx=2, pady=5, side="left")
        frame22.pack(side="top")
        frame25 = ttk.Frame(self.step3)
        frame25.configure(height=200, width=200)
        label19 = ttk.Label(frame25)
        label19.configure(text='Regularisation:')
        label19.pack(padx=2, pady=5, side="left")
        entry12 = ttk.Entry(frame25)
        entry12.configure(width=10)
        entry12.pack(padx=2, pady=5, side="left")
        frame25.pack(side="top")
        frame26 = ttk.Frame(self.step3)
        frame26.configure(height=200, width=200)
        button6 = ttk.Button(frame26)
        button6.configure(text='Save Image')
        button6.pack(padx=2, pady=5, side="left")
        frame26.pack(side="top")
        self.step3.pack(expand=True, fill="both", side="top")
        self.deconPSF_settings.pack(expand=True, fill="both", side="left")
        self.deconPSF_plot = ttk.Frame(self.deconPsfFrame)
        self.deconPSF_plot.configure(height=200, width=600)
        canvas1 = tk.Canvas(self.deconPSF_plot)
        canvas1.configure(background="#c0c0c0", borderwidth=2, width=200)
        canvas1.pack(expand=True, fill="y", padx=5, pady=20, side="left")
        canvas4 = tk.Canvas(self.deconPSF_plot)
        canvas4.configure(background="#c0c0c0", width=200)
        canvas4.pack(expand=True, fill="y", padx=5, pady=20, side="left")
        canvas6 = tk.Canvas(self.deconPSF_plot)
        canvas6.configure(background="#c0c0c0", width=200)
        canvas6.pack(expand=True, fill="y", padx=5, pady=20, side="left")
        self.deconPSF_plot.pack(expand=True, fill="both", side="right")
        self.deconPsfFrame.pack(expand=True, fill="both", side="top")

        self.deconImageFrame = ttk.Frame(self.deconNotebook)
        self.deconImageFrame.configure(height=200, width=200)

        self.deconImage_settings = ttk.Frame(self.deconPsfFrame)
        self.deconImage_settings.configure(height=200, width=200)
        self.deconImage_settings.pack(expand=True, fill="both", side="left")

        self.deconImage_plot = ttk.Frame(self.deconPsfFrame)
        self.deconImage_plot.configure(height=200, width=600)
        self.deconImage_plot.pack(expand=True, fill="both", side="right")

        self.deconImageFrame.pack(expand=True, fill="both", side="top")

        self.deconNotebook.add(self.deconPsfFrame, text = "PSF deconvolution")
        self.deconNotebook.add(self.deconImageFrame, text = "Image deconvolution")

        self.logOutputLabel = ttk.Label(self.deconPsfToplevel)
        self.logOutStringVar = tk.StringVar(value='Log Output')
        self.logOutputLabel.configure(
            compound="top",
            text='Log Output',
            textvariable=self.logOutStringVar)
        self.logOutputLabel.pack(fill="x", side="bottom")
        self.logOutputLabel.bind("<1>", self.callback, add="")

        # Main widget
        self.mainwindow = self.deconPsfToplevel

    def run(self):
        self.mainwindow.mainloop()

    def callback(self, event=None):
        pass


if __name__ == "__main__":
    app = DeconPsfView()
    app.run()
