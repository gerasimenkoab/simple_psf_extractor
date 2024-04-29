
# from common.base_controller import BaseController
import logging
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

if __name__ == "__main__":
    import tkinter as tk
    from base_model import BaseModel
    from base_view import BaseView
    model = BaseModel(None)
    view = BaseView(root = tk.Tk(), controller = None, title = "test app")
    controller = BaseController(view, model)
    view.mainloop()