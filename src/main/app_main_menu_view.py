import tkinter as tk
from tkinter import ttk
import common.PackageManager as PackageManager

class AppMainMenu(tk.Menu):
    def __init__(self, parentWindow,availablePackages = []):
        super().__init__(parentWindow)
        self.parentWindow = parentWindow
        # Create a submenu for the File section
        self.file_menu = tk.Menu(self, tearoff=0)
        self.file_menu.add_command( label="Open", command=self.open_file )
        self.file_menu.add_command( label="Save", command=self.save_file )
        self.file_menu.add_separator()
        self.file_menu.add_command( label="Close", command = self.close_application )

        self.add_cascade(label="File", menu=self.file_menu)

        # Create a submenu for the Modules section
        self.modulesMenu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Modules", menu=self.modulesMenu)

        # Add each package to the menu
        for package in availablePackages:
            self.addModuleMenuEntry(package)

        # Create a submenu for the Help section
        self.help_menu = tk.Menu(self, tearoff=0)
        self.help_menu.add_command(label="About", command=self.show_about)
        self.add_cascade(label="Help", menu=self.help_menu)


    def addModuleMenuEntry(self, package):
        self.modulesMenu.add_command(label=package, command=lambda: self.parentWindow.event_generate(f"<<Module-{package}>>"))

    def close_application(self):
        print("Closing App...")
        self.parentWindow.event_generate("<<CloseApp>>")

    def open_file(self):
        print("Opening file...")
        self.parentWindow.event_generate("<<Main-OpenFile>>")

    def save_file(self):
        print("Saving file...")
        self.parentWindow.event_generate("<<Main-SaveFiler>>")

    def show_about(self):
        print("Showing about...")
        tk.messagebox.showinfo("About", "Deconvolutor and Extractor are in Modules Menu.")
        self.parentWindow.event_generate("<<Main-Help>>")