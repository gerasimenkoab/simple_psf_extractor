#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk

class HeaderButtonFrame(ttk.Frame):
    def __init__(self, master=None, widgets=None, frameName="Image"):
        super().__init__(master)
        self.grid(column=0, row=0)
        widgets = {} if widgets is None else widgets
        self.imageFrameLbl = ttk.Label( self, text = frameName )
        self.imageFrameLbl.pack(side="top")

        self.imageLoad_btn = ttk.Button(self, text = 'Load ' + frameName, width = 15)
        widgets[frameName+"LoadButton"] = self.imageLoad_btn
        self.imageLoad_btn.pack(padx=2, pady=2, side="top")

        self.imageInfo_lbl = ttk.Label(self)
        self.imageInfoStr = tk.StringVar( value = 'No ' + frameName + ' Loaded' )
        widgets[frameName+"InfoStringVar"] = self.imageInfoStr
        self.imageInfo_lbl.configure(
            text='No Image Loaded',
            textvariable=self.imageInfoStr)
        self.imageInfo_lbl.pack(padx=2, pady=2, side="top")



class BodyFrame(ttk.Frame):
    def __init__(self, master=None, widgets=None, frameName="Image"):
        super().__init__(master)
        self.grid(column=0, row=1)
        widgets = {} if widgets is None else widgets
        self.image_cnv = tk.Canvas(self)
        widgets[frameName+"Canvas"] = self.image_cnv
        self.image_cnv.configure(
            background="#c0c0c0",
            height=350,
            insertbackground="#c0c0c0",
            insertborderwidth=0,
            width=350)
        self.image_cnv.pack(expand=True, fill="both", padx=2, pady=2)
        # layer switch
        self.imageOptionsFrame = ttk.Frame(self)
        self.imageOptionsFrame.configure(height=200, width=200)

        self.imageLayerSwitch = ttk.Frame(self.imageOptionsFrame)
        self.imageLayerSwitch.configure(height=200, width=200)
        self.imageLayer_lbl = ttk.Label(self.imageLayerSwitch)
        self.imageLayer_lbl.configure(state="normal", text='Z Layer')
        self.imageLayer_lbl.pack(anchor="s", padx=2, pady=2, side="left")
        self.imageLayer_spinbox = ttk.Spinbox(self.imageLayerSwitch)
        widgets[frameName+"LayerSpinbox"] = self.imageLayer_spinbox
        self.imageLayer_spinbox.configure(
            from_=0, increment=1, justify="center", to=100, width=4)
        _text_ = '0'
        self.imageLayer_spinbox.delete("0", "end")
        self.imageLayer_spinbox.insert("0", _text_)
        self.imageLayer_spinbox.pack(anchor="s", padx=2, pady=2, side="left")
        self.imageLayerSwitch.pack(
            expand=True,
            fill="both",
            padx=2,
            pady=2,
            side="top")
        self.imageOptionsFrame.pack()

class HeaderSelectionFrame(ttk.Frame):
    def __init__(self, master=None, widgets=None, optionsList:list = None, frameName:str = "Image" ):
        super().__init__(master)
        self.grid(column=4, row=0)
        widgets = {} if widgets is None else widgets
        self.resFrame_lbl = ttk.Label(self, text = frameName )
        self.resFrame_lbl.pack(side="top")

        self.methodFrame = ttk.Frame(self)
        self.methodFrame.configure(height=200, width=200)
        self.deconMethod_lbl = ttk.Label(self.methodFrame)
        self.deconMethod_lbl.configure(text='Method:', width=9)
        self.deconMethod_lbl.pack(padx=2, side="left")
        self.deconMethod = tk.StringVar()
        widgets[frameName+"MethodStringVar"] = self.deconMethod
        self.deconMethod_combobox = ttk.Combobox(
            self.methodFrame,
            textvariable=self.deconMethod,
            values = [] if optionsList is None else optionsList,
            state="readonly")

        self.deconMethod_combobox.configure(width=25)
        self.deconMethod_combobox.pack(side="left")
        self.decon_progbar = ttk.Progressbar(self.methodFrame)
        widgets[frameName+"ProgressBar"] = self.decon_progbar
        self.decon_progbar.configure(length=50, orient="horizontal")
        self.decon_progbar.pack(padx=2, pady=2, side="left")
        self.deconStart_btn = ttk.Button(self.methodFrame)
        widgets[frameName+"StartButton"] = self.deconStart_btn
        self.deconStart_btn.configure(text='Start', width=10)
        self.deconStart_btn.pack(padx=2, pady=2, side="left")
        self.methodFrame.pack(expand=True, fill="x", side="top")
        self.settingsFrame = ttk.Frame(self)
        self.settingsFrame.configure(height=200, width=200)
        self.deconIter_lbl = ttk.Label(self.settingsFrame)
        self.deconIter_lbl.configure(text='Iteration Number:')
        self.deconIter_lbl.pack(padx=2, side="left")
        self.deconIter_entry = ttk.Entry(self.settingsFrame)
        widgets[frameName+"IterationEntry"] = self.deconIter_entry
        self.deconIter_entry.configure(width=5)
        _text_ = '1'
        self.deconIter_entry.delete("0", "end")
        self.deconIter_entry.insert("0", _text_)
        self.deconIter_entry.pack(padx=2, side="left")
        self.deconReg_lbl = ttk.Label(self.settingsFrame)
        self.deconReg_lbl.configure(text=' Regularization:')
        self.deconReg_lbl.pack(padx=2, side="left")
        self.deconReg_entry = ttk.Entry(self.settingsFrame)
        widgets[frameName+"RegularisationEntry"] = self.deconReg_entry
        self.deconReg_entry.configure(width=8)
        _text_ = '0.000001'
        self.deconReg_entry.delete("0", "end")
        self.deconReg_entry.insert("0", _text_)
        self.deconReg_entry.pack(padx=2, side="left")
        self.resSave_btn = ttk.Button(self.settingsFrame)
        self.resSave_btn.configure(text='Save Result', width=10)
        self.resSave_btn.pack(expand=True, padx=2, pady=2, side="left")
        widgets[frameName+"SaveButton"] = self.resSave_btn
        self.settingsFrame.pack(expand=True, fill="x", side="top")
        
        
 

class DeconvolveImageFrame(ttk.Frame):
    def __init__(self, master=None, widgets = None, deconMethodsDict=None,):
        super().__init__(master)
        self._deconMethodsDict = deconMethodsDict or {
            "Richardson-Lucy": "RL",
            "Richardson-Lucy TM Reg": "RLTMR",
            "Richardson-Lucy TV Reg": "RLTVR"
        }
        widgets = {} if widgets is None else widgets

        self.configure(height=600, takefocus=True, width=600)

        # 3 columns for Image, PSF and Result:

        self.headerImageFrame = HeaderButtonFrame(self, widgets = widgets, frameName="Image")
        self.headerImageFrame.grid(column=0, row=0)

        self.imageFrame = BodyFrame(self, widgets = widgets, frameName="Image")
        self.imageFrame.grid(column=0, row=1,sticky="nsew")

        ttk.Separator(self, orient="vertical").grid(column=1, ipady=200, padx=1, row=0, rowspan=2)

        self.headerPsfFrame = HeaderButtonFrame(self, widgets = widgets, frameName="PSF")
        self.headerPsfFrame.grid(column=2, row=0)

        self.psfFrame = BodyFrame(self, widgets = widgets, frameName="PSF")
        self.psfFrame.grid(column=2, row=1,sticky="nsew")

        ttk.Separator(self, orient="vertical").grid(column=3, ipady=200, padx=1, row=0, rowspan=2)

        self.headerResFrame = HeaderSelectionFrame( self, widgets = widgets, 
                                                    optionsList = list(self._deconMethodsDict.keys()),
                                                    frameName="Result" )
        self.headerResFrame.grid(column=4, row=0)
        self.resultFrame = BodyFrame(self, widgets = widgets, frameName="Result")
        self.resultFrame.grid(column=4, row=1, sticky="nsew")


        self.grid(column=0, row=0, sticky="nsew")
        self.grid_anchor("center")

        self.rowconfigure(0, uniform=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, pad=1, uniform=1, weight=2)
        self.columnconfigure(2, pad=1, uniform=1, weight=1)
        self.columnconfigure(4, pad=1, uniform=1, weight=2)

    def DeconLoadImage_clb(self, event=None):
        pass

    def callback(self, event=None):
        pass


    def DeconPSF_clb(self, event=None):
        pass

    def DeconStart_clb(self, event=None):
        pass

    def SaveDeconImage_clb(self, event=None):
        pass

    def ResLayer_spDown(self, event=None):
        pass

    def ResLayer_spUp(self, event=None):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    #set root width and height
    root.geometry("1080x600")
    widget = DeconvolveImageFrame(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()
