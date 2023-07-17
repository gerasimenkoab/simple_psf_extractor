from tkinter.filedialog import askopenfilenames
from model.decon_psf_model import DeconPsfModel
from model.decon_image_model import DeconImageModel
from view.decon_view import DeconView
import logging

# TODO: log string output
class DeconController:
    def __init__(self, master) -> None:
        super().__init__()
        # setup logger
        self.logger = logging.getLogger("__main__." + __name__)

        self._master = master

        self.modelDeconPSF = DeconPsfModel()
        self.modelDeconImage = DeconImageModel()
        self.viewDecon = DeconView(self._master)

        self.viewDecon.SetVoxelValues(self.modelDeconPSF.PSFImage.voxel)
        self.viewDecon.SetBeadSize(self.modelDeconPSF.beadDiameter)
        # binding buttons and entries events
        self._bindDeconPSF()
        self._bindDeconImage()
        self.logger.debug("PSF and Image deconvolution controller initialized")

    def _bindDeconPSF(self):
        """
        Binding events for PSF deconvolution 
        """
        self.viewDecon.deconPsfView.loadPSF_btn.bind("<1>", self.LoadBead_btn_click, add="")
        self.viewDecon.deconPsfView.beadSize_entry.bind("<Enter>", self.UpdateBeadSizeValue, add="")
        self.viewDecon.deconPsfView.beadSize_entry.bind("<FocusOut>", self.UpdateBeadSizeValue, add="")
        for key in ["X","Y","Z"]:
            self.viewDecon.deconPsfView.voxel_entry[key].bind("<Enter>", self.UpdateBeadVoxelValues, add="")
            self.viewDecon.deconPsfView.voxel_entry[key].bind("<FocusOut>", self.UpdateBeadVoxelValues, add="")
        self.viewDecon.deconPsfView.psfReg_entry.bind("<Enter>", self.UpdatePsfReglValue, add="")
        self.viewDecon.deconPsfView.psfReg_entry.bind("<FocusOut>", self.UpdatePsfReglValue, add="")
        self.viewDecon.deconPsfView.calcPSF_btn.bind("<1>", self.CalcPSF_btn_click, add="")
        self.viewDecon.deconPsfView.savePsf_btn.bind("<1>", self.SavePSF_btn_click, add="")

    def _bindDeconImage(self):
        """
        Binding events for Image deconvolution 
        """
        self.viewDecon.deconImageView.imageLoad_btn.bind("<1>", self.DeconLoadImage_clb, add="")
        self.viewDecon.deconImageView.psfLoad_btn.bind("<1>", self.DeconPSFLoad_clb, add="")
        self.viewDecon.deconImageView.imageLayer_spinbox.bind("<<Decrement>>", self.ImageLayer_spDown, add="")
        self.viewDecon.deconImageView.imageLayer_spinbox.bind("<<Increment>>", self.ImageLayer_spUp, add="")
        self.viewDecon.deconImageView.deconStart_btn.bind("<1>", self.DeconStart_clb, add="")
        self.viewDecon.deconImageView.resSave_btn.bind("<1>", self.SaveDeconImage_clb, add="")
        self.viewDecon.deconImageView.resLayer_spinbox.bind("<<Decrement>>", self.ResLayer_spDown, add="")
        self.viewDecon.deconImageView.resLayer_spinbox.bind("<<Increment>>", self.ResLayer_spUp, add="")

    # Decon PSF Callbacks
    def LoadBead_btn_click(self,event):
        """Loading bead photo from file"""
        eventWgt = event.widget
        # fNames = askopenfilenames(parent = eventWgt, title="Load Bead Photo")
        try:
            fNames = self.viewDecon.GetFileNamesList(eventWgt,"Load Bead Photo")
        except:
            return
        try:
            self.modelDeconPSF.SetPSFImage(fNames)
        except ValueError as vE:
            if vE.args[1] == "voxel_problem":
                try:
                    voxText = "Enter voxel size as z,x,y in \u03BCm"
                    self.modelDeconPSF.SetPSFImage(fNames, self.viewDecon.GetVoxelDialog(eventWgt, voxText) )
                except ValueError as vE1:
                    raise ValueError(vE1.args[0], vE1.args[1])
            elif vE.args[1] == "data_problem":
                raise ValueError(vE.args[0], vE.args[1])
            else:
                raise ValueError(vE.args[0], vE.args[1])
        # self.modelDeconPSF.PSFImage.ShowClassInfo()
        self.viewDecon.SetFileInfoDeconPSF(self.modelDeconPSF.PSFImage.GetImageInfoStr(output = "full") )
        self.viewDecon.SetBeadImage(self.modelDeconPSF.PSFImage.imArray)
        self.logger.info("Bead File Loaded: " + fNames[0])
        
    def UpdateBeadSizeValue(self, event=None):
        pass

    def UpdateBeadVoxelValues(self, event=None):
        pass

    def UpdatePsfIterlValue(self, event=None):
        pass

    def UpdatePsfReglValue(self, event=None):
        pass

    def CalcPSF_btn_click(self, event=None):
        pass

    def SavePSF_btn_click(self, event=None):
        pass

    # Decon Image Callbacks
    def DeconLoadImage_clb(self, event=None):
        """Loading image for deconvolution from file"""
        eventWgt = event.widget
        try:
            fNames = self.viewDecon.GetFileNamesList(eventWgt,"Load Image")
        except:
            return
        try:
            self.modelDeconImage.SetDeconImage(fNames)
        except ValueError as vE:
            if vE.args[1] == "voxel_problem":
                try:
                    voxText = "Enter voxel size as z,x,y in \u03BCm"
                    self.modelDeconImage.SetDeconImage(fNames, self.viewDecon.GetVoxelDialog(eventWgt, voxText) )
                except ValueError as vE1:
                    raise ValueError(vE1.args[0], vE1.args[1])
            elif vE.args[1] == "data_problem":
                raise ValueError(vE.args[0], vE.args[1])
            else:
                raise ValueError(vE.args[0], vE.args[1])
        self.viewDecon.SetFileInfoImageDeconImage(self.modelDeconImage.deconImage.GetImageInfoStr(output = "full") )
        self.viewDecon.SetBeadImage(self.modelDeconImage.deconImage.imArray)
        self.logger.info("Bead File Loaded: " + fNames[0])

    def ImageLayer_spDown(self, event=None):
        pass

    def ImageLayer_spUp(self, event=None):
        pass

    def DeconPSFLoad_clb(self, event=None):
        """Loading PSF for deconvolution from file"""
        eventWgt = event.widget
        try:
            fNames = self.viewDecon.GetFileNamesList(eventWgt,"Load PSF")
        except:
            return
        try:
            self.modelDeconImage.SetDeconPsf(fNames)
        except ValueError as vE:
            if vE.args[1] == "voxel_problem":
                try:
                    voxText = "Enter voxel size as z,x,y in \u03BCm"
                    self.modelDeconImage.SetDeconPsf(fNames, self.viewDecon.GetVoxelDialog(eventWgt, voxText) )
                except ValueError as vE1:
                    raise ValueError(vE1.args[0], vE1.args[1])
            elif vE.args[1] == "data_problem":
                raise ValueError(vE.args[0], vE.args[1])
            else:
                raise ValueError(vE.args[0], vE.args[1])
        self.viewDecon.SetFileInfoPsfDeconImage(self.modelDeconImage.deconPsf.GetImageInfoStr(output = "full") )
        self.viewDecon.DrawDeconPsf(self.modelDeconImage.deconPsf.imArray)
        self.logger.info("Bead File Loaded: " + fNames[0]) 
        pass

    def DeconStart_clb(self, event=None):
        pass

    def SaveDeconImage_clb(self, event=None):
        pass

    def ResLayer_spDown(self, event=None):
        pass

    def ResLayer_spUp(self, event=None):
        pass


    # TODO : remove clicker test
    def buttonClickTest(self):
        print("clicked")
