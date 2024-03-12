from tkinter import Tk,Toplevel,Menu
from typing import Union # to use for the double type hinting

class EditorMenuBar(Menu):
    """Editor menu bar class. It is a subclass of tkinter.Menu."""
    def __init__(self, master:Union[Tk,Toplevel] = None, **kwargs):
        super().__init__(master, **kwargs)

        filemenu = Menu(self, tearoff=0)
        self.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(
            label="Load Image",
            underline=0,
            accelerator="Ctrl+o",
            command=lambda: master.event_generate("<<LoadImageInEditor>>"),
        )
        filemenu.add_command(
            label="Save Image",
            underline=0,
            accelerator="Ctrl+s",
            command=lambda: master.event_generate("<<SaveImageInEditor>>"),
        )
        filemenu.add_separator()
        filemenu.add_command(
            label="Close",
            command=lambda: master.event_generate("<<CloseEditor>>"),
        )

        helpMenu = Menu(self, tearoff=0)
        self.add_cascade(label="Help", menu=helpMenu)
        helpMenu.add_command(
            label="Help", command=lambda: master.event_generate("<<ShowEditorHelp>>")
        )