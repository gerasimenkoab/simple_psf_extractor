import tkinter as tk
import BeadExtractionGUI_class as BEGUI_cls
import DeconvolutionGUI_class as DeGUI_cls


class main_window_gui(tk.Tk):
    def __init__(self, master=None, width = 300, height = 250):
        super().__init__()
        self.title("Simple experimental PSF extractor")
        tk.Label(self, text = "Avialable Widgets:").pack(side = 'top',pady=10)
        b1 = tk.Button(self, text="Launch Bead Extractor Widget", command = lambda: self.OpenBeadExtractor())
        b1.pack(fill='x', side = 'top',padx=20,pady=10)
        b2 = tk.Button(self, text="Launch Deconvolution Widget", command = lambda: self.OpenDeconvolution())
        b2.pack(fill='x', side = 'top',padx=20,pady=10)
        b3 = tk.Button( self, text = "Launch NN Deconvolution Widget", command = lambda: self.OpenNNDeconvolution())
        b3.pack(fill='x', side = 'top',padx=20,pady=10)
        tk.ttk.Separator().pack(fill='x',side='top',pady=10)
        b_authors = tk.Button(self,text= 'Authors', command = lambda:self.Authors())
        b_authors.pack(side = 'left',padx = 20, pady = 10)
        b_exit = tk.Button(self,text = "Exit", command = lambda:self.CloseApplication())
        b_exit.pack(side = 'right',padx = 20, pady=10)

    def OpenBeadExtractor(self):
        """Loadding Extractor widget window"""
        child1 = BEGUI_cls.BeadExtractionGUI(self)
        child1.grab_set()
        pass

    def OpenDeconvolution(self):
        """Loadding Deconvolution widget window"""
        child2 = DeGUI_cls.DeconvolutionGUI(self)
        pass

    def OpenNNDeconvolution(self):
        """Loadding NN deconvolution widget window"""
        pass

    def Authors(self):
        """Loadding Authors List widget window"""
        child = tk.Toplevel()
        tk.Label(child, text="").grid(row=0, column=0)
        tk.Label(child, text="AUTHORS").grid(row=1, column=5)
        tk.Label(child, text="").grid(row=2, column=0)

        tk.Label(child, text="Chukanov V.").grid(row=3, column=1)
        tk.Label(child, text="").grid(row=3, column=2)
        tk.Label(child, text="Pchitskaya E.").grid(row=3, column=3)
        tk.Label(child, text="").grid(row=3, column=4)

        tk.Label(child, text="").grid(row=3, column=6)
        tk.Label(child, text="Gerasimenko A.").grid(row=3, column=7)
        tk.Label(child, text="").grid(row=3, column=8)
        tk.Label(child, text="Sachuk A.").grid(row=3, column=9)
        tk.Label(child, text="").grid(row=3, column=10)

        tk.Label(child, text="").grid(row=4, column=0)
    
    def CloseApplication(self):
        self.quit()

if __name__=="__main__":
    root_win = main_window_gui()
    root_win.mainloop()