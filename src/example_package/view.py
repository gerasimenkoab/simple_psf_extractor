import tkinter as tk
from common.base_view import BaseView

class View(BaseView):
    def __init__(self, root=None, controller=None, title = "App", wWidth:int = 800, wHeight:int= 600) -> None:
        super().__init__(root, controller, title, wWidth, wHeight)
        self.widgets["labelMessage"] = tk.Label(self, text="Number for model x^2:", bg="white", font=("Arial", 12))
        self.widgets["labelMessage"].pack(padx=2, pady=2)
        self.widgets["entryNumber"] = tk.Entry(self, bg="white", font=("Arial", 12))
        self.widgets["entryNumber"].pack(padx=2, pady=2)
        self.widgets["labelControllerMessage"] = tk.Label(self, text="Model response", bg="white", font=("Arial", 12))
        self.widgets["labelControllerMessage"].pack(padx=2, pady=2)
        self.widgets["entryModelResponse"] = tk.Entry(self, bg="white", font=("Arial", 12))
        self.widgets["entryModelResponse"].configure(state="readonly")
        self.widgets["entryModelResponse"].pack(padx=2, pady=2)
        self.widgets["closeButton"] = tk.Button(self, text="Close", command=self.destroy)
        self.widgets["closeButton"].pack(side = "bottom",padx=2, pady=2)
        self.update_idletasks()
        self.lift()

if __name__ == "__main__":
    root = tk.Tk()
    view = View(root, None)
    view.mainloop()