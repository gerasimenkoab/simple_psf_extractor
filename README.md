# simple_psf_extractor
implemintation of simple extractor of experimental PSF

TODO:

- deconvolution revision:
+ RL TM regularisation ... done
+ add method selection for PSF deconvolution app
+ add progress bar to GUI
+ add method selection for Image deconvolution app

- implement temporary file using tempfile.SpooledTemporaryFile
- logging with logger.(from logging.handlers import RotatingFileHandler)
- think about interface with ttk.Notebook() for DeconvolutionGUI -  two parts, two notebooks
- Voxel size rework. partly done. need to finish  in first part of deconvolution_gui 
- RLTV method update according to article
- TM method