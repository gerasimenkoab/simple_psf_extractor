import tkinter as tk
from tkinter.messagebox import askokcancel, showerror
from tkinter.filedialog import askopenfilenames,  askdirectory, asksaveasfilename
from tkinter.simpledialog import askstring
import os
from extractor_model import ExtractorModel
from extractor_view import ExtractorView

class ExtractorController:
    """
    pass actions and data from gui to model and back
    """    
    def __init__(self, master = None):
        self._master = master
        self.model = ExtractorModel()
        self.view = ExtractorView( self._master )
        self._beadPrevNum = 0

        self.view.SetVoxelValues(self.model.mainImage.voxel)
        self.view.SetBeadSize(self.model.beadDiameter)
        self.view.SetSelectionFrameSize(2 * self.model.selectionFrameHalf)
        # binding buttons and entries events                    
        self._bind()


   # TODO : remove clicker test
    def buttonClickTest(self):
        print("clicked")

 
    def _bind(self):
        """binding all events"""
        #buttons:

        self.view.loadBeadsPhoto_btn.config(command = self.LoadsBeadPhoto)
        self.view.undoMark_btn.config(command = self.UndoMark)
        self.view.clearMarks_btn.config(command = self.ClearMarks)
        self.view.extractBeads_btn.config(command = self.ExtractBeads)
        self.view.saveExtractedBeads_btn.config(command = self.SaveExtractedBeads)
        self.view.processBeads_btn.config(command = self.ProcessBeads)
        self.view.saveAverageBead_btn.config(command = self.SaveAverageBead)
        self.view.averageSeveralBeads_btn.config(command = self.AverageSeveralBeads)
        self.view.viewBead2d_btn.config(command = self.ViewBead2D)
        self.view.viewBead3d_btn.config(command = self.ViewBead3D)
        self.view.close_btn.config(command = self.CloseExtractor)
        print("Binding buttons... Done")
        #entries bind at two events:
        self.view.mainPhotoCanvas.bind("<Button-3>", self.BeadMarkOnClick)
        for key in ("Z","Y","X"):
            self.view.voxelSizeEntries[key].bind("<FocusOut>",self.UpdateMainImageVoxelValue)
            self.view.voxelSizeEntries[key].bind("<Return>", self.UpdateMainImageVoxelValue)
        self.view.beadSizeEntry.bind("<FocusOut>", self.UpdateBeadSizeValue)
        self.view.beadSizeEntry.bind("<Return>", self.UpdateBeadSizeValue)
        self.view.selectSizeEntry.bind("<FocusOut>", self.UpdateSelectionSizeEntry)
        self.view.selectSizeEntry.bind("<Return>", self.UpdateSelectionSizeEntry)
        self.view.beadPrevNum.bind("<FocusOut>", self.SetBeadPrevNum)
        self.view.beadPrevNum.bind("<Return>", self.SetBeadPrevNum)
        print("Binding Entries...  Done.")

    def GetVoxelDialog(self, text = ""):
        """
        Create diealog and return list of values
        """
        voxelStr = askstring("Voxel Dialog", text)
        return [float(a) for a in voxelStr.split(",")]

    def LoadsBeadPhoto(self):
        """Loading raw beads photo from file"""
        fNames = askopenfilenames(title="Load Beads Photo")
        try:
            self.model.SetMainImage(fNames)
        except ValueError as vE:
            if vE.args[1] == "voxel_problem":
                try:
                    tmpList = self.GetVoxelDialog("Enter voxel size as z,x,y in \u03BCm")
                    self.model.SetMainImage(fNames, tmpList)
                except ValueError as vE1:
                    raise ValueError(vE1.args[0],vE1.args[1])
            elif vE.args[1] == "data_problem":
                raise ValueError(vE.args[0],vE.args[1])
            else:
                raise ValueError(vE.args[0],vE.args[1])
        self.model.BeadCoordsClear()
        self.model.mainImage.ShowClassInfo()
        try:
            self.model.mainImage.SaveAsTiff(filename="tmp.tiff")
            self.view.SetMainPhotoImage("tmp.tiff")
            self.view.SetVoxelValues(self.model.mainImage.voxel)
        except:
            raise IOError("Cant update GUI properly")        

    def ClearMarks(self):
        self.view.BeadMarksClear()
        self.model.BeadCoordsClear()

    def UndoMark(self):
        self.view.BeadMarksRemoveLast()
        self.model.BeadCoordsRemoveLast()

    def ExtractBeads(self):
        self.model.MarkedBeadsExtract()

    def SaveExtractedBeads(self):
        try:
            dirPath = askdirectory()
        except:
            dirPath = ""
        self.model.ExtractedBeadsSave( dirPath )

    def ProcessBeads(self):
        self.model.BeadsArithmeticMean()
        self.model.BlurAveragedBead( self.view.blurApplyType.get() )

    def SaveAverageBead(self):
        self.model.SaveAverageBead( asksaveasfilename() )
        pass

    def AverageSeveralBeads(self):
        # self.model.
        pass

    def ViewBead2D(self):
        pass

    def ViewBead3D(self):
        pass

    def CloseExtractor(self):
        """Closing window and clear tmp files"""
        # Checking existance of self.imgBeadsRaw.close()
        if askokcancel("Close", "Close Bead Extractor Widget?"):
            try:
                self.view.imgBeadsRaw.close()
            except:
                print("Can't close imgBeadsRaw image")
            tmppath = os.getcwd() + "\\tmp.tiff"
            try:
                os.remove(tmppath)
            except:
                raise FileNotFoundError( tmppath )
            self.view.destroy()

    def BeadMarkOnClick(self,event):
        """
        Append mouse event coordinates to global list. Center is adjusted according to max intensity.
        """
        cnv = event.widget
        xClick, yClick = cnv.canvasx(event.x), cnv.canvasy(event.y)
        xr, yr = self.model.LocateFrameMAxIntensity3D(xClick, yClick)
        halfSide = self.model.selectionFrameHalf
        self.view.beadMarks.append(
            cnv.create_rectangle(
                xr - halfSide,
                yr - halfSide,
                xr + halfSide,
                yr + halfSide,
                outline="chartreuse1",
                width=2,
            )
        )
        self.model._beadCoords.append([xr, yr])
        self.view.beadCoords.append([xr, yr])


    def UpdateMainImageVoxelValue(self):
        try:
            newVoxel = [ float( self.view.voxelSizeEntries["Z"].get()),
                float( self.view.voxelSizeEntries["Y"].get()),
                float( self.view.voxelSizeEntries["X"].get()) ]
            self.model.SetVoxelSize(newVoxel)
        except:
            raise ValueError("Can not update voxel values.", "cant_update_voxel")

    def UpdateBeadSizeValue(self):
        self.model.beadDiameter = float( self.view.beadSizeEntry.get() )

    def UpdateSelectionSizeEntry(self):
        self.model.selectionFrameHalf = int( self.view.selectSizeEntry.get() ) * 2

    def SetBeadPrevNum(self):
        self._beadPrevNum = int( self.view.beadPrevNum.get() )





    def GetData(self):
        """Get data from all forms"""
        self.data ={
            "voxel" : GetVoxel,
            "beadSize" : GetBeadSize,
            "selectionSize" : GetSelectionSize,
            "tiffType" : "uint8",
            "blurType:" : "none",
            "previewTick" : False,
        }


        for idField, vField in enumerate(self.voxelFields):
            tmp = self.voxelSizeEntries[vField].get()
            try:
                self.beadVoxelSize[idField] = abs( float(tmp) )
                if self.beadVoxelSize[idField] < zeroTreshold:
                    self.beadVoxelSize[idField] = zeroTreshold
            except:
                showerror("Set Voxel Size: ", "Bad input: not a Float.")
                self.voxelSizeEntries[vField].delete(0, END)
                self.voxelSizeEntries[vField].insert(0, self.beadVoxelSize[idField])
                return

if __name__ == "__main__":
    root = tk.Tk()
    ExtractorController(root)
    root.mainloop()
        
# забиндить ивенты ко всем виджетам и для них сделать функции, обрабатывающие приходящие данные из форм.
# Buttons:   LoadBeadsPhoto, self.loadBeadsPhoto_btn
#            UndoMark, self.undoMark_btn
#            ClearAllMark, self.clearMarks_btn
#            ExtractSelectedBeads, self.extractBeads_btn
#            SaveExtractedBeads, self.saveExtractedBeads_btn
#            ProcessExtractedBeads, self.processBeads_btn
#            SaveAverageBead, self.saveAverageBead_btn
#            AverageSeveralBeads, self.AverageSeveralBeads_btn
#            Bead2D, self.bead2d_btn
#            Bead3D, self.bead3d_btn
#            close, self.close_btn
# total 10

# Entry:     voxel_Z, voxel_z
#            voxel_Y, voxel_y
#            voxel_X, voxel_z
#            beadSize, self.beadSizeEntry
#            SelectionSize, self.selectSizeEntry
#            beadNumber, self.beadPrevNum
# total 6

# Get value with get() when needed.
# Menu: blurType, self.blurApplyType
#       tiffType, self.tiffType_menu
# Tickbox: preview, self.precessBeadPrev
