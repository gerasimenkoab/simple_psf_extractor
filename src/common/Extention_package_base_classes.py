import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import logging
from typing import Dict

try: # if running from main
    from common.LogTextHandler_class import LogTextHandler
except: # if running from test
    from LogTextHandler_class import LogTextHandler

class BaseController:
    def __init__(self, viewFromExemplar = None, modelFromExamplar = None) -> None:
        # setup logger
        self.logger = logging.getLogger("__main__." + __name__)

        try:
            self.model = modelFromExamplar
        except Exception as e:
            self.logger.error("Can't create  model. "+str(e))
            raise ValueError("Can't create model", "model-creation-failed")
        
        try:
            self.view = viewFromExemplar
        except Exception as e:
            self.logger.error("Can't create GUI view. "+str(e))
            raise ValueError("Can't create GUI view", "view-creation-failed")

        self.SetLogOutput()
        self.bindEvents()

    def bindEvents(self):
        pass
        # self.view.getWidget("closeButton").bind("<Button-1>", self.onClose) 


    def SetLogOutput(self):
        self.handler =  LogTextHandler(self.view.getWidget("logWidget"))  
        self.handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        self.handler.setFormatter(formatter)    
        self.logger.addHandler(self.handler)

    def onClose(self, event):
        self.logger.info("Closing widget")
        self.view.destroy()



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


class BaseModel:
    def __init__(self, controller) -> None:
        self.logger = logging.getLogger("__main__." + __name__)
        self.controller = controller
        self.logger.info("Model created")
        pass

    def modelMethod(self):
        self.logger.info("Model method called")
        pass


if __name__ == "__main__":
    import tkinter as tk
    model = BaseModel(None)
    view = BaseView(root = tk.Tk(), controller = None, title = "test app")
    controller = BaseController(view, model)
    view.mainloop()