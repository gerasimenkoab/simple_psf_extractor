import deconvolutor.decon_controller as decon_controller
import tkinter as tk

def Run(parent=None):
    if parent is None:
        parent = tk.Tk()       
    decon_controller.DeconController(parentView = parent)

if __name__=="__main__":
    pass