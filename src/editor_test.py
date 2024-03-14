import tkinter as tk
import ctypes
from tkinter import ttk
from editor.editor_view import EditorView

"""Driver for testing EditorView class"""

if __name__ == "__main__":

    # need to SetProcessDPIAware to get correct resolution numbers for both TK and user32 method.
    user32 = ctypes.windll.user32
    # user32.SetProcessDPIAware()
    root = tk.Tk()
    root.title("Editor view testing")
    quitBtn = ttk.Button(root, text="Quit", command=root.quit).pack(side=tk.TOP,fill=tk.X)
    # print("Tk screen dimensions:", root.winfo_screenwidth(), root.winfo_screenheight())
    # print("user32 screen dimensions:", user32.GetSystemMetrics(78), user32.GetSystemMetrics(79))
    winWidth = user32.GetSystemMetrics(78)/4
    winHeight = user32.GetSystemMetrics(79)/3
    base1 = EditorView(root, winWidth, winHeight)
    base1.mainloop()