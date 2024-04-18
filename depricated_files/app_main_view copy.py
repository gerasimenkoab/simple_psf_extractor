import tkinter as tk
import tkinter.ttk as ttk
import logging
import ctypes
from main.app_main_menu_view import AppMainMenu


class MainAppView(tk.Tk):
    def __init__(self, masterController = None,  wWidth = 300, wHeight = 250):
        super().__init__()

        self.logger = logging.getLogger('__main__.'+__name__)
        user32 = ctypes.windll.user32
        setDPIAware = False
        if setDPIAware:
            user32.SetProcessDPIAware()
            self.logger.info("App DPI Awareness set to True")
        else:
            self.logger.info("App DPI Awareness set to False")

        self.logger.info("TK Screen dimensions: %s x %s", self.winfo_screenwidth(), self.winfo_screenheight())
        self.logger.info("user32 Screen dimensions: %s x %s", user32.GetSystemMetrics(78), user32.GetSystemMetrics(79))
        
        self.title("Simple PSF")

        # create window menu bar    
        self.menu = AppMainMenu(self)
        self.config(menu=self.menu)



        ttk.Label(self, text = "Avialable Utilites:").pack(side = 'top',pady=10)
        
        self.b1 = ttk.Button(self, text="Bead Extractor ", command = lambda: self.event_generate("<<RunBeadExtractorWidget>>"))
        self.b1.pack(fill='x', side = 'top',padx=20,pady=10)

        self.b2 = ttk.Button(self, text="Deconvolutor ", command = lambda: self.event_generate("<<RunDeconvolutionWidget>>"))
        self.b2.pack(fill='x', side = 'top',padx=20,pady=10)
        
        self.b3 = ttk.Button( self, text = "NN Deconvolutor ", command = lambda: self.event_generate("<<RunNNDeconvolutionWidget>>"))
        self.b3.pack(fill='x', side = 'top',padx=20,pady=10)
        
        ttk.Separator().pack(fill='x',side='top',pady=10)
        b_authors = ttk.Button(self,text= 'Authors', command = lambda:self.event_generate("<<ShowAuthors>>"))
        b_authors.pack(side = 'left',padx = 20, pady = 10)
        b_exit = ttk.Button(self,text = "Exit", command = lambda:self.event_generate("<<CloseApplication>>"))
        b_exit.pack(side = 'right',padx = 20, pady=10)


        

    def ShowAuthors(self):
        """Loadding Authors List widget window"""
        child = tk.Toplevel(self)
        child.title("Authors")
        ttk.Label(child, text="").grid(row=0, column=0)
        ttk.Label(child, text="").grid(row=2, column=0)

        ttk.Label(child, text="Gerasimenko A., ").grid(row=3, column=1)
        ttk.Label(child, text="").grid(row=3, column=2)
        ttk.Label(child, text="Sachuk A., Zolin I.").grid(row=3, column=3)
        ttk.Label(child, text="").grid(row=3, column=4)

        ttk.Label(child, text="").grid(row=3, column=6)
        ttk.Label(child, text= "Chukanov V., ").grid(row=3, column=7)
        ttk.Label(child, text="").grid(row=3, column=8)
        ttk.Label(child, text="Pchitskaya E.").grid(row=3, column=9)
        ttk.Label(child, text="").grid(row=3, column=10)

        ttk.Label(child, text="").grid(row=4, column=0)
