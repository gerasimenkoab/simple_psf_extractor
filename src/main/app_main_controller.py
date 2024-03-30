from tkinter.filedialog import askopenfilenames, asksaveasfilename
from tkinter.simpledialog import askstring
import logging

import tkinter as tk
import tkinter.ttk as ttk
from main.app_main_view import MainAppView
from main.app_main_model import MainAppModel
# from cnn.cnn_deconvolution_gui import *
import logging

class MainAppController():
    def __init__(self, master=None):
        self.logger = logging.getLogger('__main__.'+__name__)
        self.logger.info("Main App started.")
        try:
            self.model = MainAppModel()
        except Exception as e:
            self.logger.error("Can't create model. "+str(e))
            raise ValueError("Can't create model", "model-creation-failed")
        
        try:
            self.view = MainAppView()
        except Exception as e:
            self.logger.error("Can't create GUI. "+str(e))
            raise ValueError("Can't create GUI", "GUI-creation-failed")
        # try set image to view
        try:
            self.view.setLayerNumber(self.model.GetVisibleLayerNumber())
            self.view.SetImageColor(self.model.GetImageColor())
            self.view.DrawImageOnCanvas(self.model.GetVisibleLayerImage())
        except Exception as e:          
            self.logger.error("Can't set image to GUI. "+str(e))
            raise ValueError("Can't set image to GUI", "view-image-setting-failed")
        self.view.SetImageInfo("Not loaded")
        self.view.SetStatusBarMessage(" Loaded image parameters: " + self.model.mainImageRaw.GetImageInfoStr(output = "full"))

        # binding buttons and entries events
        self._bind()


    def _bind(self):
        """binding all events"""
        # menus:
        # File:
        self.view.bind("<<Main-OpenFile>>",self.LoadsBeadPhoto)
        self.view.bind("<Control-o>",self.LoadsBeadPhoto)
        self.view.bind("<<Main-SaveFiler>>",self.SaveImage)
        self.view.bind("<<Control-s>>",self.SaveImage)
        self.view.bind("<<CloseApp>>",self.CloseApplication)
        # Help:
        self.view.bind("<<ShowHelp>>",self.ShowExtractorHelp)

        # buttons:
        self.view.bind("<<LayerUp>>", self.VisibleLayerUp)
        self.view.bind("<<LayerDown>>", self.VisibleLayerDown)
        self.view.bind("<<CropSelected>>", self.CropSelected)

        #options menu:
        self.view.bind("<<ImageColorChanged>>", self.OnImageColorChange)

        # scalers events binding:
        self.view.bind("<<BrightnessScaleChanged>>", self.OnScaleChangeEventHandler)
        self.view.bind("<<ContrastScaleChanged>>", self.OnScaleChangeEventHandler)
        self.view.bind("<<ImageScaleChanged>>", self.OnScaleChangeEventHandler)

        # entries bind at two events:
        self.logger.info("_bind: Binding buttons and entries is done.")

    def Run(self):
        self.view.mainloop()
        self.logger.info("Main App running.")

    def CropSelected(self, event=None):
        """Crop selected area of image"""
        try:
            self.model.CropSelectedArea(self.view.GetCropBox())
        except Exception as e:
            self.logger.error("Can't crop image. "+str(e))
            raise ValueError("Can't crop image", "image-cropping-failed")
        self.view.DrawImageOnCanvas(self.model.GetVisibleLayerImage())
        self.view.setLayerNumber(self.model.GetVisibleLayerNumber())
        self.logger.info("Image cropped.")

    def ShowExtractorHelp(self, event=None):
        """Show help window"""
        raise NotImplementedError("ShowExtractorHelp")
    
    def SaveImage(self, event=None):
        """Adjust image according to current brightness and contrast settings and save it to file"""
        fname = asksaveasfilename( parent = self.view, title="Save Image",
                                   filetypes=[("TIFF files", "*.tiff")],
                                   defaultextension=".tiff" )
        outBitType = self.view.GetTiffBitType()
        if fname is None:
            return
        try:
            self.model.SaveImageAsTiff(fname, outBitType)
        except Exception as e:
            self.logger.error("Can't save image. "+str(e))
            raise ValueError("Can't save image", "image-saving-failed")
        self.logger.info("Image saved as tiff. "+fname)

    def OnScaleChangeEventHandler(self, event=None):
        brightnessValue,contrastValue = self.view.GetScalersValues()
        self.model.SetBrightnessValue(brightnessValue)
        self.model.SetContrastValue(contrastValue)
        self.view.DrawImageOnCanvas(self.model.GetVisibleLayerImage())

    # def OnScaleChangeEventHandler(self, event=None):
    #     self.view.DrawImageOnCanvas(self.model.GetVisibleLayerImage())        

    def OnImageColorChange(self, event=None):
        self.model.SetImageColor(self.view.GetImageColor())
        self.view.DrawImageOnCanvas(self.model.GetVisibleLayerImage())

    def VisibleLayerUp(self, event=None):
        self.model.VisibleLayerNumberUp()
        self.view.DrawImageOnCanvas(self.model.GetVisibleLayerImage())
        self.view.setLayerNumber(self.model.GetVisibleLayerNumber())


    def VisibleLayerDown(self, event=None):
        self.model.VisibleLayerNumberDown()
        self.view.DrawImageOnCanvas(self.model.GetVisibleLayerImage())
        self.view.setLayerNumber(self.model.GetVisibleLayerNumber())


    def GetVoxelDialog(self, text=""):
        """
        Create diealog and return list of values
        """
        voxelStr = askstring("Voxel Dialog", text)
        return [float(a) for a in voxelStr.split(",")]

    def LoadsBeadPhoto(self, event=None):
        """Loading raw beads photo from file"""
        fNames = askopenfilenames( title="Load Beads Photo")
        if fNames is None:
            self.logger.debug("File list from dialog is empty. "+fNames[0])
            raise ValueError("No file name recieved", "filename_empty")
        try:
            self.model.SetMainImage(fNames)
        except ValueError as vE:
            if vE.args[1] == "voxel_problem":
                self.logger.debug("No voxel info recieved. Open voxel input dialog.")
                try:
                    tmpList = self.GetVoxelDialog( "Enter voxel size as z,x,y in \u03BCm"  )
                    print("recieved:", tmpList)
                except Exception as e:
                    self.logger.debug("file(s) load failed. "+ str(e))
                    raise ValueError("Can not get voxel info from dialog", "voxel-dialog-fail")
                self.logger.debug("From dialog recieved: "+str(tmpList))
                try:
                    self.model.SetMainImage(fname=fNames, voxel = tmpList, array = None)
                except ValueError as vE1:
                    self.logger.error("file(s) load failed. Can not use voxel info from dialog ")
                    raise ValueError("Can not use voxel info from dialog", "voxel-dialog-fail")
            elif vE.args[1] == "data_problem":
                self.logger.error("file(s) load failed. "+fNames[0])
                raise ValueError(vE.args[0], vE.args[1])
            else:
                self.logger.error("file(s) load failed. "+fNames[0])
                raise ValueError("Unknown error", "unknown-error")
        self.logger.info("File loaded. ")


        # visualization:
        try:
            self.view.DrawImageOnCanvas(self.model.GetVisibleLayerImage())
        except Exception as e:
            self.logger.error("Draw image  " + str(e))
            raise IOError("Cant update GUI properly")
        self.view.SetImageInfo(fNames[0])
        self.view.SetStatusBarMessage(self.model.mainImageRaw.GetImageInfoStr(output = "full"))
        self.view.setLayerNumber(self.model.GetVisibleLayerNumber())


    def CloseApplication(self,event=None):
        self.view.quit()
        self.logger.info("Application Closed.")









