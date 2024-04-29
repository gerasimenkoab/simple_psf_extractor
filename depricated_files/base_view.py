import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import logging
from typing import Dict

class BaseView(tk.Toplevel):
    def __init__(self, root=None, controller=None, title = "App", wWidth:int = 800, wHeight:int= 600) -> None:

        self.logger = logging.getLogger("__main__." + __name__)
        self.root = root
        self.controller = controller

        super().__init__(self.root, bg="white",width=wWidth, height=wHeight)
        self.title( title )
        self.widgets: Dict[str, tk.Widget] = {}
        self.imgCnv: Dict[str,tk.Image] = {}
        self.sourceCanvasImage: Dict[str, tk.Image] = {}

        self.widgets["logWidget"] = self.CreateLogWidget()
        self.widgets["logWidget"].pack(fill="x", side = "bottom",padx=2, pady=2)
        # self.widgets["closeButton"] = tk.Button(self, text="Close", command=self.destroy)
        # self.widgets["closeButton"].pack(side = "bottom",padx=2, pady=2)

        self.logger.info("View created")
        self.update_idletasks()
        self.lift()


    def getWidget(self, widgetName):
        return self.widgets[widgetName]

    def CreateLogWidget(self)->ScrolledText:      
        logWidget = ScrolledText(self, wrap = tk.WORD, height = 2)
        logWidget.configure(state = "disabled")
        return logWidget

    def onError(self, error):
        messagebox.showerror("Error", error)

if __name__ == "__main__":
    root = tk.Tk()
    view = BaseView(root, None)
    view.mainloop()