from deconvolutor.decon_psf_model import DeconPsfModel
from deconvolutor.decon_image_model import DeconImageModel
from deconvolutor.decon_view import DeconView
from editor.editor_controller import EditorController
import logging

# TODO: log string output
class DeconController:
    def __init__(self, parentView) -> None:
        # super().__init__()
        # setup logger
        self.logger = logging.getLogger("__main__." + __name__)
        self._master = parentView
        try:
            self.modelDeconPSF = DeconPsfModel()
        except Exception as e:
            self.logger.error("Can't create PSF deconvolution model. "+str(e))
            raise ValueError("Can't create PSF deconvolution model", "model-creation-failed")
        
        try:
            self.modelDeconImage = DeconImageModel()
        except Exception as e:
            self.logger.error("Can't create Image deconvolution model. "+str(e))
            raise ValueError("Can't create Image deconvolution model", "model-creation-failed")
        
        try:
            self.viewDecon = DeconView(self._master)
        except Exception as e:
            self.logger.error("Can't create Deconvolution view. "+str(e))
            raise ValueError("Can't create Deconvolution view", "view-creation-failed")
        
        self.viewDecon.SetVoxelValues(self.modelDeconPSF.PSFImage.GetVoxelDict())
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
        self.viewDecon.deconPsfView.beadSize_entry.bind("<Return>", self.UpdateBeadSizeValue, add="")
        self.viewDecon.deconPsfView.beadSize_entry.bind("<FocusOut>", self.UpdateBeadSizeValue, add="")
        for key in ["X","Y","Z"]:
            self.viewDecon.deconPsfView.voxel_entry[key].bind("<Return>", self.UpdateBeadVoxelValues, add="")
            self.viewDecon.deconPsfView.voxel_entry[key].bind("<FocusOut>", self.UpdateBeadVoxelValues, add="")
        self.viewDecon.deconPsfView.psfIterNum_entry.bind("<Return>", self.UpdatePsfIterlValue, add="")
        self.viewDecon.deconPsfView.psfIterNum_entry.bind("<FocusOut>", self.UpdatePsfIterlValue, add="")
        self.viewDecon.deconPsfView.psfReg_entry.bind("<Return>", self.UpdatePsfReglValue, add="")
        self.viewDecon.deconPsfView.psfReg_entry.bind("<FocusOut>", self.UpdatePsfReglValue, add="")
        self.viewDecon.deconPsfView.calcPSF_btn.bind("<1>", self.CalcPSF_btn_click, add="")
        self.viewDecon.deconPsfView.savePsf_btn.bind("<1>", self.SavePSF_btn_click, add="")
        self.viewDecon.deconPsfView.zoomFactor_entry.bind("<Return>", self.UpdateZoomFactorValue, add="")
        self.viewDecon.deconPsfView.zoomFactor_entry.bind("<FocusOut>", self.UpdateZoomFactorValue, add="")


    def _bindDeconImage(self):
        """
        Binding events for Image deconvolution 
        """
        try:
            #buttons click events
            self.viewDecon.widgets["ImageLoadButton"].bind("<1>", self.DeconLoadImage_clb, add="")
            self.viewDecon.widgets["PSFLoadButton"].bind("<1>", self.DeconPSFLoad_clb, add="")
            self.viewDecon.widgets["ResultStartButton"].bind("<1>", self.DeconStart_clb, add="")
            self.viewDecon.widgets["ResultSaveButton"].bind("<1>", self.DeconImageEditor_clb, add="")
            # Entry change events
            self.viewDecon.widgets["ResultIterationEntry"].bind("<Return>", self.UpdateImageIterlValue, add="")
            self.viewDecon.widgets["ResultIterationEntry"].bind("<FocusOut>", self.UpdateImageIterlValue, add="")
            self.viewDecon.widgets["ResultRegularisationEntry"].bind("<Return>", self.UpdateImageReglValue, add="")
            self.viewDecon.widgets["ResultRegularisationEntry"].bind("<FocusOut>", self.UpdateImageReglValue, add="")
            # Spinbox change events
            for target in ["Image","PSF","Result"]:
                self.viewDecon.widgets[target+"LayerSpinbox"].bind("<Return>", 
                                                                lambda event: self.LayerChangeSpinbox(event, "enter", target))
                self.viewDecon.widgets[target+"LayerSpinbox"].bind("<<Decrement>>", 
                                                                lambda event: self.LayerChangeSpinbox(event, "down", target))
                self.viewDecon.widgets[target+"LayerSpinbox"].bind("<<Increment>>", 
                                                                lambda event: self.LayerChangeSpinbox(event, "up", target))
        except Exception as e:
            self.logger.error("Can't bind events for Image deconvolution. "+str(e))
            raise ValueError("Can't bind events for Image deconvolution", "binding-failed")
        
    # ======= Decon PSF Callbacks ===============
    def LoadBead_btn_click(self,event):
        """Loading bead photo from file"""
        eventWgt = event.widget
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
        self.viewDecon.SetBeadImage(self.modelDeconPSF.PSFImage.GetIntensities())
        self.viewDecon.SetVoxelValues(self.modelDeconPSF.PSFImage.GetVoxelDict())
        self.logger.info("Bead File Loaded: " + fNames[0])
        
    def UpdateBeadSizeValue(self, event=None):
        eventWgt = event.widget
        try:
            newValue = float( eventWgt.get() )
        except:
            self.viewDecon.SetValueWidgetNormal( eventWgt, self.modelDeconPSF.beadDiameter )
            return
        try:
            self.modelDeconPSF.beadDiameter = newValue
        except:
            self.viewDecon.SetValueWidgetNormal( eventWgt, self.modelDeconPSF.beadDiameter )
            return
        self.viewDecon.SetValueWidgetNormal( eventWgt, newValue )


    def UpdateZoomFactorValue(self, event=None):
        eventWgt = event.widget
        try:
            newValue = float( eventWgt.get() )  
        except:
            self.viewDecon.SetValueWidgetNormal( eventWgt, self.modelDeconPSF.zoomFactor )
            return
        self.viewDecon.SetValueWidgetNormal( eventWgt, newValue )

    def UpdateBeadVoxelValues(self, event=None):
        eventWgt = event.widget
        axisName = eventWgt.name
        try:
            newValue = float( eventWgt.get() )
        except:
            self.viewDecon.SetValueWidgetNormal( eventWgt, self.modelDeconPSF.voxel[axisName] )
            return
        try:
            self.modelDeconPSF.SetVoxelByAxis(axisName, newValue)
        except Exception as e:
            self.viewDecon.SetValueWidgetNormal( eventWgt, self.modelDeconPSF.voxel[axisName] )
            return
        self.viewDecon.SetValueWidgetNormal( eventWgt, newValue )

        pass



    def UpdatePsfIterlValue(self, event=None):
        eventWgt = event.widget
        try:
            newValue = int( eventWgt.get() )
        except:
            self.viewDecon.SetValueWidgetNormal( eventWgt, self.modelDeconPSF.iterationNumber )
            return
        try: 
            self.modelDeconPSF.iterationNumber = newValue
        except:
            self.viewDecon.SetValueWidgetNormal( eventWgt, self.modelDeconPSF.iterationNumber )
            return
        self.viewDecon.SetValueWidgetNormal( eventWgt, newValue )

    def UpdatePsfReglValue(self, event=None):
        eventWgt = event.widget
        try:
            newValue = float( eventWgt.get() )
        except:
            self.viewDecon.SetValueWidgetNormal( eventWgt, self.modelDeconPSF.regularizationParameter )
            return
        try: 
            self.modelDeconPSF.regularizationParameter = newValue
        except:
            self.viewDecon.SetValueWidgetNormal( eventWgt, self.modelDeconPSF.regularizationParameter )
            return
        self.viewDecon.SetValueWidgetNormal( eventWgt, newValue )

    def CalcPSF_btn_click(self, event=None):
        progBar = self.viewDecon.GetPsfDeconProgressbar()
        method = self.viewDecon.GetPsfDeconMethod()
        self.logger.info("Starting bead deconvolution. Method code: " + method)
        try:
            self.modelDeconPSF.CalculatePSF( method, progBar, self.viewDecon )
        except Exception as e:
            self.logger.info("Bead deconvolution failed with exception: " + str(e))
            return
        try:
            self.viewDecon.SetPSFImage( self.modelDeconPSF.resultImage.GetIntensities() )
        except:
            return
        self.logger.info("Bead image deconvolution finished.")


    def SavePSF_btn_click(self, event=None):

        if self.modelDeconPSF.resultImage == None:
            self.logger.info("Can not save. PSF was not created.")
            return
        try:
            fName = self.viewDecon.GetFileName(event.widget,"Select file name")
        except:
            return
        try:
            self.modelDeconPSF.resultImage.SaveAsTiff(fName)
        except ValueError as vE:
           self.logger.debug(str(vE[0]))
           return
        self.logger.info("PSF was saved as " + fName)

    # ======== Decon Image Callbacks ===============================

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
                    try:
                        voxelRead =  self.viewDecon.GetVoxelDialog(eventWgt, voxText) 
                    except:
                        self.logger.info("Bad voxel info in dialog.")
                        return
                    self.modelDeconImage.SetDeconImage(fNames, voxelRead)
                except ValueError as vE1:
                    self.logger.info("Image load failed.")
                    return
            elif vE.args[1] == "data_problem":
                self.logger.info("Image load failed. Bad intesity array. ")
                return
            else:
                self.logger.info("Image load failed. Unknown problem.")
                return
        self.viewDecon.widgets["ImageLayerSpinbox"].set(self.modelDeconImage.GetVisibleLayerNumberFor("Image"))
        self.viewDecon.SetFileInfoImageDeconImage(self.modelDeconImage.GetInfoStringFor("Image") )
        self.viewDecon.DrawImageOnCanvas(canvasName = "Image",img = self.modelDeconImage.GetVisibleLayerImageFor("Image"))
        self.logger.info("Bead File Loaded: " + fNames[0])



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
        self.viewDecon.widgets["PSFLayerSpinbox"].set(self.modelDeconImage.GetVisibleLayerNumberFor("PSF"))
        self.viewDecon.SetFileInfoPsfDeconImage(self.modelDeconImage.GetInfoStringFor("PSF") )
        self.viewDecon.DrawImageOnCanvas(canvasName = "PSF",img = self.modelDeconImage.GetVisibleLayerImageFor("PSF"))
        self.logger.info("PSF File Loaded: " + fNames[0]) 


    def LayerChangeSpinbox(self, event = None, action:str = "", canvasName:str = "Image")->None:
        """Change visible layer number for Image, PSF or Result canvas 
            at action 'up', 'down' or 'enter' 
            on corresponding spinbox widget."""
        
        if action not in ["up", "down","enter"] :
            raise ValueError("Wrong action", "action-incorrect")
        
        if action in [ "up","down"]:
            self.logger.debug("Action up/down at " + canvasName)
            self.modelDeconImage.VisibleLayerChange(action,canvasName)
        else:
            self.logger.debug("Action enter at " + canvasName)
            wgt = event.widget
            try:
                spValue = int(wgt.get())
                self.modelDeconImage.SetVisibleLayerNumberFor(canvasName, spValue)      
            except:
                self.logger.debug("Can't change layer number at " + canvasName)
                wgt.set(str(self.modelDeconImage.GetVisibleLayerNumberFor(canvasName)))
                raise            
        try:
            self.viewDecon.DrawImageOnCanvas(canvasName = canvasName,img = self.modelDeconImage.GetVisibleLayerImageFor(canvasName) )
        except:
            self.logger.debug("Can't draw image at " + canvasName)
            raise



    # def ImageLayerChange(self, wgt = None, name:str = "Image"):
    #     try:
    #         spValue = int(wgt.get())
    #         self.modelDeconImage.SetVisibleLayerNumberFor(name, spValue)      
    #         self.viewDecon.DrawImageOnCanvas(canvasName = name,image = self.modelDeconImage.GetVisibleLayerImageFor(name) )
    #     except:
    #         wgt.set(str(self.modelDeconImage.GetVisibleLayerNumberFor(name)))
    #         return

    # def ImageLayerChange_clb(self,event = None):
    #     wgt = event.widget
    #     self.ImageLayerChange(self, wgt, name = "Image")

    # def PSFLayerChange_clb(self,event = None):
    #     wgt = event.widget
    #     self.ImageLayerChange(self, wgt, name = "PSF")

    # def ResLayerChange_clb(self,event = None):
    #     wgt = event.widget
    #     self.ImageLayerChange(self, wgt, name = "Result")

    def UpdateImageIterlValue(self, event=None):
        eventWgt = event.widget
        try:
            newValue = int( eventWgt.get() )
        except:
            self.viewDecon.SetValueWidgetNormal( eventWgt, self.modelDeconImage.iterationNumber )
            return
        try: 
            self.modelDeconImage.iterationNumber = newValue
        except:
            self.viewDecon.SetValueWidgetNormal( eventWgt, self.modelDeconImage.iterationNumber )
            return
        self.viewDecon.SetValueWidgetNormal( eventWgt, newValue )

    def UpdateImageReglValue(self, event=None):
        eventWgt = event.widget
        try:
            newValue = float( eventWgt.get() )
        except:
            self.viewDecon.SetValueWidgetNormal( eventWgt, self.modelDeconImage.regularizationParameter )
            return
        try: 
            self.modelDeconImage.regularizationParameter = newValue
        except:
            self.viewDecon.SetValueWidgetNormal( eventWgt, self.modelDeconImage.regularizationParameter )
            return
        self.viewDecon.SetValueWidgetNormal( eventWgt, newValue )




    def DeconStart_clb(self, event=None):
        try:
            progBar = self.viewDecon.GetDeconImageProgressbar()
            method = self.viewDecon.GetImageDeconMethod()
        except Exception as e:
            self.logger.debug("Can not get parameters for deconvolution. " + str(e))
            return
        decon_wgt = self.modelDeconImage
        self.logger.info("Starting image deconvolution. Method code: " + method)
        
        try:
            self.modelDeconImage.DeconvolveImage( method, progBar, self.viewDecon )
        except Exception as e:
            self.logger.info("Image deconvolution failed."+str(e))
            return


        try:

            self.viewDecon.widgets["ResultLayerSpinbox"].set(self.modelDeconImage.GetVisibleLayerNumberFor("Result"))
            self.viewDecon.SetFileInfoPsfDeconImage(self.modelDeconImage.GetInfoStringFor("Result") )
            self.viewDecon.DrawImageOnCanvas(canvasName = "Result",img = self.modelDeconImage.GetVisibleLayerImageFor("Result"))
            # self.viewDecon.widgets["ResultLayerSpinbox"].configure( from_=0, to = decon_wgt.deconResult.GetImageShape()[0]-1 )
            # layerId = int(self.viewDecon.widgets["ResultLayerSpinbox"].get())
            # self.viewDecon.DrawResultImage(decon_wgt.deconResult.GetIntensitiesLayer(layerId))
        except Exception as e:
            self.logger.debug("Can not draw deconvolution resulting image. " + str(e))
            return
        self.logger.info("Image deconvolution finished.")
        
    def SaveDeconImage_clb(self, event=None):
        if self.modelDeconImage.deconResult == None:
            self.logger.info("File not saved. Deconvolution result image was not created.")
            return
        try:
            fName = self.viewDecon.GetFileName(event.widget,"Select file name")
        except:
            return
        try:
            self.modelDeconImage.deconResult.SaveAsTiff(fName)
        except ValueError as vE:
           self.logger.debug(str(vE[0]))
           return
        self.logger.info("Result image was saved as " + fName)

    def DeconImageEditor_clb(self, event=None):
        if self.modelDeconImage.deconResult == None:
            self.logger.info("File not saved. Deconvolution result image was not created.")
            return
        # Open Image Editor with deconResult ImageRaw object
        try:
            self.editor = EditorController(self.viewDecon, self.modelDeconImage.deconResult.mainImageRaw)
        except Exception as e:
            self.logger.debug("Can not open image editor. " + str(e))
            return