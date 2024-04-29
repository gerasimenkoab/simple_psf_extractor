import tkinter as tk
# from common.base_controller import BaseController
import logging
from common.base_controller import BaseController

from example_package.view  import View
from example_package.model import Model

class Controller(BaseController):
    def __init__(self, masterView = None) -> None:
        # super().__init__()
        # setup logger
        self.logger = logging.getLogger("__main__." + __name__)

        if masterView is None:
            self._masterView = tk.Tk()
        else:
            self._masterView = masterView
        # create model and view
        try:
            self.model = Model(self)
        except Exception as e:
            self.logger.error("Can't create  model. "+str(e))
            raise ValueError("Can't create model", "model-creation-failed")
        
        try:
            self.view = View(root = self._masterView, controller = self, title = "Widget Name")
        except Exception as e:
            self.logger.error("Can't create GUI view. "+str(e))
            raise ValueError("Can't create GUI view", "view-creation-failed")
        # init Base controller
        super().__init__(self.view, self.model)
        # bind events
        self.bindEvents()

    def bindEvents(self):
        self.view.getWidget("entryNumber").bind("<Return>", self.onEnter)
        self.view.getWidget("entryNumber").bind("<FocusOut>", self.onEnter)
        self.view.getWidget("closeButton").bind("<Button-1>", self.onClose) 

    def onEnter(self, event):
        try:
            self.logger.info("Number entered. Processing")
            number = int(self.view.getWidget("entryNumber").get())
            response = self.model.processNumber(number)
            self.logger.info("Number processed. Showing response")
            self.view.getWidget("entryModelResponse").configure(state="normal")
            self.view.getWidget("entryModelResponse").delete(0, tk.END)
            self.view.getWidget("entryModelResponse").insert(0, response)
            self.view.getWidget("entryModelResponse").configure(state="readonly")
        except ValueError as e:
            self.view.onError("Invalid number. Please enter a valid number.")
            self.logger.error("Invalid number. Please enter a valid number.")
        except Exception as e:
            self.view.onError("Error processing number. "+str(e))
            self.logger.error("Error processing number. "+str(e))

        
    def onClose(self, event):
        self.logger.info("Closing application")
        self._masterView.destroy()

# if __name__ == "__main__":
#     controller = Controller()
#     controller.bindEvents()
#     controller.view.mainloop()