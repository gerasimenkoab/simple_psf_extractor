import os
import pkgutil
import importlib
import configparser

class PackageManager:

    # Define the packages you want to include in packages.conf file in the project directory

    def __init__(self):
        self._allowedPackages = ['extractor']
        self._availablePackages = []
        # Get the path to the project directory where your packages are located
        self._project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.loadAllowedPackages(os.path.join(self._project_dir, 'packages.conf'))
        self.setAvailablePackages()
        # print(f"Available packages: {self._availablePackages}")
        # print(f"Allowed packages: {self._allowedPackages}")

    def loadAllowedPackages(self, filename):
        config = configparser.ConfigParser()
        config.read(filename)
        packages = config.get('packages', 'names')
        self._allowedPackages = [package.strip() for package in packages.split(',')]

    def getAllowedPackages(self):
        return self._allowedPackages

    def setAvailablePackages(self):
         # Get a list of all available packages in the project directory
        self._availablePackages = [name for _, name, is_pkg in pkgutil.iter_modules([self._project_dir]) if is_pkg and name in self._allowedPackages]

    def getAvailablePackages(self):
        return self._availablePackages

    def loadModule(self, package_name, master=None):
        #run module main
        print(f"Loading module: {package_name}")
        main_module = importlib.import_module(f"{package_name}.main")
        main_module.Run(master)


