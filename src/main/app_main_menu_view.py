import pkgutil
import os
import tkinter as tk
from tkinter import ttk
import importlib

class AppMainMenu(tk.Menu):
    def __init__(self, parentWindow):
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
        self.modules_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Modules", menu=self.modules_menu)

       # Get the path to the project directory where your packages are located
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Define the packages you want to include
        allowed_packages = ['deconvolutor',  'extractor']

        # Get a list of all available packages in the project directory
        available_packages = [name for _, name, is_pkg in pkgutil.iter_modules([project_dir]) if is_pkg and name in allowed_packages]

        # Add each package to the menu
        for package in available_packages:
            self.modules_menu.add_command(label=package, command=lambda pkg=package: self.load_module(pkg))

        # Create a submenu for the Help section
        self.help_menu = tk.Menu(self, tearoff=0)
        self.help_menu.add_command(label="About", command=self.show_about)
        self.add_cascade(label="Help", menu=self.help_menu)

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
        tk.messagebox.showinfo("About", "This is a simple application")
        self.parentWindow.event_generate("<<Main-Help>>")

    def load_module(self, package_name):
        print(f"Loading module: {package_name}")
        main_module = importlib.import_module(f"{package_name}.main")
        main_module.Run(self.parentWindow)