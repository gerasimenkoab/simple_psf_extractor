import tkinter as tk
from tkinter.messagebox import askokcancel
from tkinter.filedialog import askopenfilenames, askdirectory, asksaveasfilename
from tkinter.simpledialog import askstring
import os
import logging

from model.extractor_model import ExtractorModel
from view.extractor_view import ExtractorView
from controller.extractor_bead_prev_controller import ExtractorBeadPreviewController


class ExtractorController:
    """
    Passing actions and data from gui to model and back
    """

    def __init__(self, master=None):
        super().__init__()
        # setup logger
        self.logger = logging.getLogger("__main__." + __name__)
        self.logger.info("Initializing Bead Extractor module.")

        self._master = master
        self.model = ExtractorModel()
        self.view = ExtractorView(self._master)

        self.view.SetVoxelValues(self.model.mainImage.voxel)
        self.view.SetBeadSize(self.model.beadDiameter)
        self.view.SetSelectionFrameSize(2 * self.model.selectionFrameHalf)
        # binding buttons and entries events
        self._bind()


    def _bind(self):
        """binding all events"""
        # menus:
        # File:
        self.view.bind("<<LoadImageDialog>>",self.LoadsBeadPhoto)
        self.view.bind("<<SaveSelectedBeads>>",self.SaveExtractedBeads)
        self.view.bind("<<SaveAverageBead>>",self.SaveAverageBead)
        self.view.bind("<<AverageSeveralBeads>>",self.AverageSeveralBeads)
        self.view.bind("<<CloseExtractor>>",self.CloseExtractor)
        # Selection:

        self.view.bind("<<UndoSelect>>",self.UndoMark)
        self.view.bind("<Control-z>",self.UndoMark)
        self.view.bind("<<ClearAllBeads>>",self.ClearMarks)
        self.view.bind("<<PreviewBeads>>",self.PreviewBeads)

        # Help:
        self.view.bind("<<ShowHelp>>",self.ShowExtractorHelp)
        # buttons:
        # self.view.loadBeadsPhoto_btn.config(command=self.LoadsBeadPhoto)
        # self.view.undoMark_btn.config(command=self.UndoMark)
        # self.view.clearMarks_btn.config(command=self.ClearMarks)
        # self.view.saveExtractedBeads_btn.config(command=self.SaveExtractedBeads)
        self.view.processBeads_btn.config(command=self.ProcessBeads)
        # self.view.saveAverageBead_btn.config(command=self.SaveAverageBead)
        # self.view.averageSeveralBeads_btn.config(command=self.AverageSeveralBeads)
        self.view.viewBead2d_btn.config(command=self.ViewBead2D)
        self.view.viewBead3d_btn.config(command=self.ViewBead3D)
        # self.view.close_btn.config(command=self.CloseExtractor)
        # entries bind at two events:
        self.view.mainPhotoCanvas.bind("<Button-3>", self.BeadMarkOnClick)
        for key in ("Z", "Y", "X"):
            self.view.voxelSizeEntries[key].bind(
                "<FocusOut>", self.UpdateMainImageVoxelValue
            )
            self.view.voxelSizeEntries[key].bind(
                "<Return>", self.UpdateMainImageVoxelValue
            )
        self.view.beadSizeEntry.bind("<FocusOut>", self.UpdateBeadSizeValue)
        self.view.beadSizeEntry.bind("<Return>", self.UpdateBeadSizeValue)
        self.view.selectSizeEntry.bind("<FocusOut>", self.UpdateSelectionSizeEntry)
        self.view.selectSizeEntry.bind("<Return>", self.UpdateSelectionSizeEntry)
        self.logger.info("_bind: Binding buttons and entries is done.")

    def ShowExtractorHelp(self):
        pass

    

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
        self.model.BeadCoordsClear()
        self.logger.info("File(s) load success. ")

        # visualization:
        try:
            self.view.SetMainPhotoImageArray(self.model.mainImage.imArray)
        except Exception as e:
            self.logger.error("LoadsBeadPhoto: can't array  " + str(e))
            raise IOError("Cant update GUI properly")
        try:
            self.view.SetVoxelValues(self.model.mainImage.voxel)
        except Exception as e:
            self.logger.error("LoadsBeadPhoto: can't set voxel values " + str(e))
            raise IOError("Cant update GUI properly")
        self.view.SetFileInfo(self.model.mainImage.GetImageInfoStr(output = "full"))

    def ClearMarks(self, event=None):
        """Clear bead marks"""
        self.view.BeadMarksClear()
        self.model.BeadCoordsClear()

    def UndoMark(self, event=None):
        """Remove the last bead mark"""
        self.view.BeadMarksRemoveLast()
        self.model.BeadCoordsRemoveLast()

    def SaveExtractedBeads(self, event=None):
        try:
            dirPath = askdirectory()
        except:
            dirPath = ""
        self.model.ExtractedBeadsSave(dirPath)

    def ProcessBeads(self, event=None):
        self.model.BeadsArithmeticMean()
        self.model.BlurAveragedBead(self.view.blurApplyType.get())
        if self.view.precessBeadPrev.get() == 1:
            self.view.PlotCanvasInWindow(self.model.averageBead.imArray)

    def SaveAverageBead(self, event=None):
        self.model.SaveAverageBead(asksaveasfilename())
        pass

    def AverageSeveralBeads(self, event=None):
        raise NotImplementedError("will do it soon")
        # TODO fix AverageManyBeads
        self.model.AverageManyBeads(
            askopenfilenames(title="Load Beads"), asksaveasfilename()
        )
        pass

    def ViewBead2D(self, event=None):
        try:
            id = self.view.beadListViewGet()
        except:
            return
        self.view.PlotBeadPreview2D(self.model._extractedBeads[id].imArray, '2D Bead plot '+ str(self.model._beadCoords[id]))

    def ViewBead3D(self, event=None):
        try:
            id = self.view.beadListViewGet()
        except:
            return
        self.view.PlotBeadPreview3D(self.model._extractedBeads[id].imArray, '3D Bead plot '+ str(self.model._beadCoords[id]))

    def CloseExtractor(self, event=None):
        """Closing window and clear tmp files"""
        # Checking existance of self.imgBeadsRaw.close()
        if askokcancel("Close", "Close Bead Extractor Widget?"):
            # try:
            #     self.view.imgBeadsRaw.close()
            # except:
            #     pass
            # # tmppath = os.getcwd() + "\\tmp.tiff"
            # try:
            #     # os.remove(tmppath)
            # except:
            #     pass
            self.view.destroy()
            self.logger.info("Bead Extractor Closed.")

    def BeadMarkOnClick(self, event=None):
        """
        Append mouse event coordinates to global list. Center is adjusted according to max intensity.
        """
        widget = event.widget
        xClick, yClick = widget.canvasx(event.x), widget.canvasy(event.y)
        if self.view.autocorrectSelection.get() == 1:
            xr, yr = self.model.LocateFrameMaxIntensity3D(xClick, yClick)
        else:
            xr, yr = xClick, yClick
        self.model.beadMarkAdd([xr, yr])
        self.view.beadMarkAdd(widget, xr, yr)

    def UpdateMainImageVoxelValue(self, event = None):
        try:
            newVoxel = [
                float(self.view.voxelSizeEntries["Z"].get()),
                float(self.view.voxelSizeEntries["Y"].get()),
                float(self.view.voxelSizeEntries["X"].get()),
            ]
            self.model.SetVoxelSize(newVoxel)
        except:
            raise ValueError("Can not update voxel values.", "cant_update_voxel")

    def UpdateBeadSizeValue(self, event=None):
        self.model.beadDiameter = float(self.view.beadSizeEntry.get())

    def UpdateSelectionSizeEntry(self, event = None):
        try:
            self.model.selectionFrameHalf = int(self.view.selectSizeEntry.get()) // 2
        except:
            self.logger.debug("Wrong selection size value.")

    def PreviewBeads(self, event=None):
        # ExtractorBeadPreviewController(self._master, self.model)
        ExtractorBeadPreviewController(self.view, self.model)

