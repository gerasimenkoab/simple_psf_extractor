from tkinter.messagebox import askokcancel, showerror
from tkinter.filedialog import askopenfilenames, askdirectory, asksaveasfilename
from tkinter.simpledialog import askstring
import logging

from editor.editor_model import EditorModel
from editor.editor_view import EditorView
from common.ImageRaw_class import ImageRaw


class EditorController:
    """
    Passing actions and data from gui to model and back
    """

    def __init__(self, masterWidget=None, image:ImageRaw = None):
        # super().__init__()
        # setup logger
        self.logger = logging.getLogger("__main__." + __name__)
        self.logger.info("Initializing Bead Extractor module.")

        try:
            self.model = EditorModel(image)
        except Exception as e:
            self.logger.error("Can't create model. "+str(e))
            raise ValueError("Can't create model", "model-creation-failed")
        
        try:
            self.view = EditorView(masterWidget)
        except Exception as e:
            self.logger.error("Can't create view. "+str(e))
            raise ValueError("Can't create view", "view-creation-failed")
        self._masterWidget = masterWidget
        # try set image to view
        try:
            self.view.SetMainPhotoImageArray(self.model.mainImage.imArray)
        except Exception as e:
            self.logger.error("Can't set image to view. "+str(e))
            raise ValueError("Can't set image to view", "view-image-setting-failed")

        # binding buttons and entries events
        self._bind()


    def _bind(self):
        """binding all events"""
        # menus:
        # File:
        self.view.bind("<<LoadImageDialog>>",self.LoadsBeadPhoto)
        self.view.bind("<Control-o>",self.LoadsBeadPhoto)
        self.view.bind("<<SaveImage>>",self.SaveImage)
        self.view.bind("<<Control-s>>",self.SaveImage)
        self.view.bind("<<CloseEditor>>",self.CloseEditor)
        # Help:
        self.view.bind("<<ShowHelp>>",self.ShowExtractorHelp)

        # buttons:
        # entries bind at two events:
        self.logger.info("_bind: Binding buttons and entries is done.")

    def ShowExtractorHelp(self, event=None):
        """Show help window"""
        raise NotImplementedError("ShowExtractorHelp")
    
    def SaveImage(self, event=None):
        """Adjust image according to current brightness and contrast settings and save it to file"""
        raise NotImplementedError("SaveImage")
    
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
        self.logger.info("File(s) load success. ")

        # visualization:
        try:
            self.view.SetMainPhotoImageArray(self.model.mainImage.imArray)
        except Exception as e:
            self.logger.error("LoadsBeadPhoto: can't array  " + str(e))
            raise IOError("Cant update GUI properly")
        self.view.SetFileInfo(self.model.mainImage.GetImageInfoStr(output = "full"))


    def CloseEditor(self, event=None):
        self.view.destroy()
        self.logger.info("Editor Closed.")

