import extractor.extractor_controller as editor_controller
import tkinter as tk

def Run(parent=None):
    if parent is None:
        parent = tk.Tk()       
    editor_controller.ExtractorController(parentView = parent)

if __name__=="__main__":
    pass