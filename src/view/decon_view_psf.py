#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk


class DeconPSFFrameNb(ttk.Frame):
    def __init__(self, master=None, **kw):
        super(DeconPSFFrameNb, self).__init__(master, **kw)
        self.deconPSF_settings = ttk.Frame(self)
        self.deconPSF_settings.configure(height=200, width=200)
        self.step1_frm = ttk.Frame(self.deconPSF_settings)
        self.step1_frm.configure(height=200, width=200)
        self.step1_lbl = ttk.Label(self.step1_frm)
        self.step1_lbl.configure(font="TkHeadingFont", text='Load Bead Image')
        self.step1_lbl.pack(pady=10, side="top")
        self.step1_load_frm = ttk.Frame(self.step1_frm)
        self.step1_load_frm.configure(height=200, width=200)
        self.loadPSF_btn = ttk.Button(self.step1_load_frm)
        self.loadPSF_btn.configure(text='Load Image')
        self.loadPSF_btn.pack(padx=5, side="left")
        self.loadPSF_btn.bind("<1>", self.LoadBead_btn_click, add="")
        self.loadPsfInfo_entry = ttk.Entry(self.step1_load_frm)
        self.loadPsfInfo_entry.configure(state="readonly")
        _text_ = 'No Image Loaded'
        self.loadPsfInfo_entry["state"] = "normal"
        self.loadPsfInfo_entry.delete("0", "end")
        self.loadPsfInfo_entry.insert("0", _text_)
        self.loadPsfInfo_entry["state"] = "readonly"
        self.loadPsfInfo_entry.pack(
            expand=True, fill="x", padx=5, pady=5, side="right")
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
        self.beadParamFrame = ttk.Frame(self.step2)
        self.beadParamFrame.configure(height=200, width=200)
        self.psfBeadSizeFrame = ttk.Frame(self.beadParamFrame)
        self.psfBeadSizeFrame.configure(height=200, width=200)
        self.beadSize_lbl = ttk.Label(self.psfBeadSizeFrame)
        self.beadSize_lbl.configure(text='Bead Size (nm):')
        self.beadSize_lbl.pack(padx=5, pady=5, side="left")
        self.beadSize_entry = ttk.Entry(self.psfBeadSizeFrame)
        self.beadSize_entry.configure(validate="focusout", width=10)
        _text_ = '0.1'
        self.beadSize_entry.delete("0", "end")
        self.beadSize_entry.insert("0", _text_)
        self.beadSize_entry.pack(padx=5, pady=5, side="left")
        self.beadSize_entry.bind("<Enter>", self.UpdateBeadSizeValue, add="")
        self.beadSize_entry.bind(
            "<FocusOut>", self.UpdateBeadSizeValue, add="")
        self.psfBeadSizeFrame.pack(side="top")
        self.psfVoxelSizeFrame = ttk.Frame(self.beadParamFrame)
        self.psfVoxelSizeFrame.configure(height=200, width=200)
        label8 = ttk.Label(self.psfVoxelSizeFrame)
        label8.configure(text='Voxel')
        label8.pack(padx=2, pady=2, side="left")
        label11 = ttk.Label(self.psfVoxelSizeFrame)
        label11.configure(text='X:')
        label11.pack(padx=2, pady=2, side="left")
        self.voxelX_entry = ttk.Entry(self.psfVoxelSizeFrame)
        self.voxelX_entry.configure(
            state="normal", validate="focusout", width=5)
        _text_ = '0.02'
        self.voxelX_entry.delete("0", "end")
        self.voxelX_entry.insert("0", _text_)
        self.voxelX_entry.pack(padx=5, pady=5, side="left")
        self.voxelX_entry.bind("<Enter>", self.UpdateBeadVoxelValues, add="")
        self.voxelX_entry.bind(
            "<FocusOut>",
            self.UpdateBeadVoxelValues,
            add="")
        label9 = ttk.Label(self.psfVoxelSizeFrame)
        label9.configure(text='Y:')
        label9.pack(padx=2, pady=2, side="left")
        self.voxelY_entry = ttk.Entry(self.psfVoxelSizeFrame)
        self.voxelY_entry.configure(
            state="normal", validate="focusout", width=5)
        _text_ = '0.02'
        self.voxelY_entry.delete("0", "end")
        self.voxelY_entry.insert("0", _text_)
        self.voxelY_entry.pack(padx=2, pady=2, side="left")
        self.voxelY_entry.bind("<Enter>", self.UpdateBeadVoxelValues, add="")
        self.voxelY_entry.bind(
            "<FocusOut>",
            self.UpdateBeadVoxelValues,
            add="")
        label10 = ttk.Label(self.psfVoxelSizeFrame)
        label10.configure(text='Z:')
        label10.pack(padx=2, pady=2, side="left")
        self.voxelZ_entry = ttk.Entry(self.psfVoxelSizeFrame)
        self.voxelZ_entry.configure(
            state="normal", validate="focusout", width=5)
        _text_ = '0.1'
        self.voxelZ_entry.delete("0", "end")
        self.voxelZ_entry.insert("0", _text_)
        self.voxelZ_entry.pack(padx=2, pady=2, side="left")
        self.voxelZ_entry.bind("<Enter>", self.UpdateBeadVoxelValues, add="")
        self.voxelZ_entry.bind(
            "<FocusOut>",
            self.UpdateBeadVoxelValues,
            add="")
        self.psfVoxelSizeFrame.pack(side="top")
        self.beadParamFrame.pack(expand=True, fill="both", side="top")
        separator3 = ttk.Separator(self.step2)
        separator3.configure(orient="horizontal")
        separator3.pack(fill="x", padx=10, pady=10, side="top")
        self.step2.pack(expand=True, fill="both", padx=5, pady=5, side="top")
        self.psfDeconParamFrame = ttk.Frame(self.deconPSF_settings)
        self.psfDeconParamFrame.configure(height=200, width=200)
        self.step3_lbl = ttk.Label(self.psfDeconParamFrame)
        self.step3_lbl.configure(text='Deconvolution parameters')
        self.step3_lbl.pack(side="top")
        self.methodFrame = ttk.Frame(self.psfDeconParamFrame)
        self.methodFrame.configure(height=200, width=200)
        label17 = ttk.Label(self.methodFrame)
        label17.configure(text='Method:')
        label17.pack(padx=2, pady=5, side="left")
        self.deconType_combobox = ttk.Combobox(self.methodFrame)
        self.deconMethodMenuStrVal = tk.StringVar()
        self.deconType_combobox.configure(
            textvariable=self.deconMethodMenuStrVal)
        self.deconType_combobox.pack(padx=2, pady=5, side="left")
        self.methodFrame.pack(side="top")
        self.psfDeconBtmFrame = ttk.Frame(self.psfDeconParamFrame)
        self.psfDeconBtmFrame.configure(height=200, width=200)
        self.deconPSF_pgbar = ttk.Progressbar(self.psfDeconBtmFrame)
        self.deconPSF_pgbar.configure(orient="horizontal")
        self.deconPSF_pgbar.pack(padx=2, pady=5, side="top")
        self.calcPSF_btn = ttk.Button(self.psfDeconBtmFrame)
        self.calcPSF_btn.configure(text='Calculate PSF')
        self.calcPSF_btn.pack(padx=2, pady=5, side="top")
        self.calcPSF_btn.bind("<1>", self.CalcPSF_btn_click, add="")
        self.psfDeconBtmFrame.pack(side="top")
        self.psfIterNumFrame = ttk.Frame(self.psfDeconParamFrame)
        self.psfIterNumFrame.configure(height=200, width=200)
        label14 = ttk.Label(self.psfIterNumFrame)
        label14.configure(text='Iteration number:')
        label14.pack(padx=2, pady=5, side="left")
        self.psfIterNum_entry = ttk.Entry(self.psfIterNumFrame)
        self.psfIterNum_entry.configure(width=10)
        self.psfIterNum_entry.pack(padx=2, pady=5, side="left")
        self.psfIterNum_entry.bind("<Enter>", self.UpdatePsfIterlValue, add="")
        self.psfIterNum_entry.bind(
            "<FocusOut>", self.UpdatePsfIterlValue, add="")
        self.psfIterNumFrame.pack(side="top")
        frame25 = ttk.Frame(self.psfDeconParamFrame)
        frame25.configure(height=200, width=200)
        label19 = ttk.Label(frame25)
        label19.configure(text='Regularisation:')
        label19.pack(padx=2, pady=5, side="left")
        self.psfReg_entry = ttk.Entry(frame25)
        self.psfReg_entry.configure(width=10)
        self.psfReg_entry.pack(padx=2, pady=5, side="left")
        self.psfReg_entry.bind("<Enter>", self.UpdatePsfReglValue, add="")
        self.psfReg_entry.bind("<FocusOut>", self.UpdatePsfReglValue, add="")
        frame25.pack(side="top")
        self.psfDeconRegFrame = ttk.Frame(self.psfDeconParamFrame)
        self.psfDeconRegFrame.configure(height=200, width=200)
        self.savePsf_btn = ttk.Button(self.psfDeconRegFrame)
        self.savePsf_btn.configure(text='Save PSF')
        self.savePsf_btn.pack(padx=2, pady=5, side="left")
        self.savePsf_btn.bind("<1>", self.SavePSF_btn_click, add="")
        self.psfDeconRegFrame.pack(side="top")
        self.psfDeconParamFrame.pack(expand=True, fill="both", side="top")
        self.deconPSF_settings.pack(expand=True, fill="both", side="left")
        self.deconPSF_plot = ttk.Frame(self)
        self.deconPSF_plot.configure(height=200, width=600)
        canvas1 = tk.Canvas(self.deconPSF_plot)
        canvas1.configure(background="#c0c0c0", borderwidth=2, width=100)
        canvas1.pack(expand=True, fill="both", padx=5, pady=20, side="left")
        canvas4 = tk.Canvas(self.deconPSF_plot)
        canvas4.configure(background="#c0c0c0", width=100)
        canvas4.pack(expand=True, fill="both", padx=5, pady=20, side="left")
        canvas6 = tk.Canvas(self.deconPSF_plot)
        canvas6.configure(background="#c0c0c0", width=100)
        canvas6.pack(expand=True, fill="both", padx=5, pady=20, side="left")
        self.deconPSF_plot.pack(expand=True, fill="both", side="right")
        self.configure(height=200, width=200)
        self.pack(expand=True, fill="both", side="top")

    def LoadBead_btn_click(self, event=None):
        pass

    def UpdateBeadSizeValue(self, event=None):
        pass

    def UpdateBeadVoxelValues(self, event=None):
        pass

    def CalcPSF_btn_click(self, event=None):
        pass

    def UpdatePsfIterlValue(self, event=None):
        pass

    def UpdatePsfReglValue(self, event=None):
        pass

    def SavePSF_btn_click(self, event=None):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = DeconPSFFrameNb(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()


# import tkinter as tk
# from tkinter import ttk

# class deconPSFFrameNb(tk.Frame):
#         """
#         Frame for deconView Notebook page dedicated to PSF deconvolution
#         """
#         def __init__(self, *args, **kwargs):
#             super().__init__(*args, **kwargs)
#         # def __init__( self, master = None ):
#         #     super().__init__( self )
#             # self = ttk.Frame( master )
#             # self.configure(height=200, width=200)
#             self.deconPSF_settings = ttk.Frame(self)
#             self.deconPSF_settings.configure(height=200, width=200)
#             self.step1_frm = ttk.Frame(self.deconPSF_settings)
#             self.step1_frm.configure(height=200, width=200)
#             self.step1_lbl = ttk.Label(self.step1_frm)
#             self.step1_lbl.configure(font="TkCaptionFont", text='Load Bead Image')
#             self.step1_lbl.pack(pady=10, side="top")
#             self.step1_load_frm = ttk.Frame(self.step1_frm)
#             self.step1_load_frm.configure(height=200, width=200)
#             self.loadPSF_btn = ttk.Button(self.step1_load_frm)
#             self.loadPSF_btn.configure(text='Load Image')
#             self.loadPSF_btn.pack(padx=5, side="left")
#             entry4 = ttk.Entry(self.step1_load_frm)
#             entry4.configure(state="readonly")
#             _text_ = 'No Image Loaded'
#             entry4["state"] = "normal"
#             entry4.delete("0", "end")
#             entry4.insert("0", _text_)
#             entry4["state"] = "readonly"
#             entry4.pack(expand=True, fill="x", padx=5, pady=5, side="right")
#             self.step1_load_frm.pack(expand=True, fill="both", padx=5, side="top")
#             self.step1_sep = ttk.Separator(self.step1_frm)
#             self.step1_sep.configure(orient="horizontal")
#             self.step1_sep.pack(
#                 expand=True,
#                 fill="x",
#                 padx=10,
#                 pady=10,
#                 side="top")
#             self.step1_frm.pack(expand=True, fill="both", side="top")
#             self.step2 = ttk.Frame(self.deconPSF_settings)
#             self.step2.configure(height=200, width=200)
#             self.step2_lbl = ttk.Label(self.step2)
#             self.step2_lbl.configure(text='Bead Parameters')
#             self.step2_lbl.pack(side="top")
#             frame16 = ttk.Frame(self.step2)
#             frame16.configure(height=200, width=200)
#             frame17 = ttk.Frame(frame16)
#             frame17.configure(height=200, width=200)
#             self.beadSize_lbl = ttk.Label(frame17)
#             self.beadSize_lbl.configure(text='Bead Size (nm):')
#             self.beadSize_lbl.pack(padx=5, pady=5, side="left")
#             self.beadSize_entry = ttk.Entry(frame17)
#             self.beadSize_entry.configure(validate="focusout", width=10)
#             self.beadSize_entry.pack(padx=5, pady=5, side="left")
#             frame17.pack(side="top")
#             frame18 = ttk.Frame(frame16)
#             frame18.configure(height=200, width=200)
#             label8 = ttk.Label(frame18)
#             label8.configure(text='Voxel')
#             label8.pack(padx=2, pady=2, side="left")
#             label11 = ttk.Label(frame18)
#             label11.configure(text='X:')
#             label11.pack(padx=2, pady=2, side="left")
#             entry6 = ttk.Entry(frame18)
#             entry6.configure(state="normal", validate="focusout", width=5)
#             entry6.pack(padx=5, pady=5, side="left")
#             label9 = ttk.Label(frame18)
#             label9.configure(text='Y:')
#             label9.pack(padx=2, pady=2, side="left")
#             entry7 = ttk.Entry(frame18)
#             entry7.configure(state="normal", validate="focusout", width=5)
#             entry7.pack(padx=2, pady=2, side="left")
#             label10 = ttk.Label(frame18)
#             label10.configure(text='Z:')
#             label10.pack(padx=2, pady=2, side="left")
#             entry8 = ttk.Entry(frame18)
#             entry8.configure(state="normal", validate="focusout", width=5)
#             entry8.pack(padx=2, pady=2, side="left")
#             frame18.pack(side="top")
#             frame16.pack(expand=True, fill="both", side="top")
#             separator3 = ttk.Separator(self.step2)
#             separator3.configure(orient="horizontal")
#             separator3.pack(fill="x", padx=10, pady=10, side="top")
#             self.step2.pack(expand=True, fill="both", padx=5, pady=5, side="top")
#             self.step3 = ttk.Frame(self.deconPSF_settings)
#             self.step3.configure(height=200, width=200)
#             label12 = ttk.Label(self.step3)
#             label12.configure(text='Deconvolution parameters')
#             label12.pack(side="top")
#             frame24 = ttk.Frame(self.step3)
#             frame24.configure(height=200, width=200)
#             label17 = ttk.Label(frame24)
#             label17.configure(text='Method:')
#             label17.pack(padx=2, pady=5, side="left")
#             combobox2 = ttk.Combobox(frame24)
#             self.deconMethodMenuStrVal = tk.StringVar()
#             combobox2.configure(textvariable=self.deconMethodMenuStrVal)
#             combobox2.pack(padx=2, pady=5, side="left")
#             frame24.pack(side="top")
#             frame20 = ttk.Frame(self.step3)
#             frame20.configure(height=200, width=200)
#             progressbar1 = ttk.Progressbar(frame20)
#             progressbar1.configure(orient="horizontal")
#             progressbar1.pack(padx=2, pady=5, side="top")
#             self.calc = ttk.Button(frame20)
#             self.calc.configure(text='Calculate PSF')
#             self.calc.pack(padx=2, pady=5, side="top")
#             frame20.pack(side="top")
#             frame22 = ttk.Frame(self.step3)
#             frame22.configure(height=200, width=200)
#             label14 = ttk.Label(frame22)
#             label14.configure(text='Iteration number:')
#             label14.pack(padx=2, pady=5, side="left")
#             entry9 = ttk.Entry(frame22)
#             entry9.configure(width=10)
#             entry9.pack(padx=2, pady=5, side="left")
#             frame22.pack(side="top")
#             frame25 = ttk.Frame(self.step3)
#             frame25.configure(height=200, width=200)
#             label19 = ttk.Label(frame25)
#             label19.configure(text='Regularisation:')
#             label19.pack(padx=2, pady=5, side="left")
#             entry12 = ttk.Entry(frame25)
#             entry12.configure(width=10)
#             entry12.pack(padx=2, pady=5, side="left")
#             frame25.pack(side="top")
#             frame26 = ttk.Frame(self.step3)
#             frame26.configure(height=200, width=200)
#             button6 = ttk.Button(frame26)
#             button6.configure(text='Save Image')
#             button6.pack(padx=2, pady=5, side="left")
#             frame26.pack(side="top")
#             self.step3.pack(expand=True, fill="both", side="top")
#             self.deconPSF_settings.pack(expand=True, fill="both", side="left")
#             self.deconPSF_plot = ttk.Frame(self)
#             self.deconPSF_plot.configure(height=200, width=600)
#             canvas1 = tk.Canvas(self.deconPSF_plot)
#             canvas1.configure(background="#c0c0c0", borderwidth=2, width=200)
#             canvas1.pack(expand=True, fill="y", padx=5, pady=20, side="left")
#             canvas4 = tk.Canvas(self.deconPSF_plot)
#             canvas4.configure(background="#c0c0c0", width=200)
#             canvas4.pack(expand=True, fill="y", padx=5, pady=20, side="left")
#             canvas6 = tk.Canvas(self.deconPSF_plot)
#             canvas6.configure(background="#c0c0c0", width=200)
#             canvas6.pack(expand=True, fill="y", padx=5, pady=20, side="left")
#             self.deconPSF_plot.pack(expand=True, fill="both", side="right")
#             self.pack(expand=True, fill="both", side="top")



