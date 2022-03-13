import pydicom
import os
import sys
from glob import glob
import numpy as np
from scipy.ndimage import gaussian_filter, rotate
from skimage.util import img_as_ubyte
from skimage.io import imsave

class DcmReader:
    """Base class for handling DICOM files
    Inputs
    ------
    path (str): Path for the file to be read

    Raises
    ------
    IncorrectNumberOfImages
        Error to be raised when the folder doesn't contain exactly two .dcm files
    SameImagePositionPatient
        Error to be raised when comparing two IPP of two images.
    """
    def __init__(self, path):
        self.pathFile = path
        self._read_file_array_iip()

    def _read_file_array_iip(self):
        """ Reads the file that was initialized    
        """        
        raw = pydicom.dcmread(self.pathFile)
        self.original = raw.pixel_array
        self.iip = self._read_iip_safe(raw)

    def _read_iip_safe(self, dcmFile):
        """Returns the Image Position Patient with checks, slower but safer

        Args:
            dcmFile (pydicom.dataset.FileDataset): Dicom file

        Returns:
            list: Three item list of Image Position Patient
        """    
        if "ImagePositionPatient" in dcmFile:
            result = list(dcmFile.ImagePositionPatient) # Should be as a 3 items list
        else:
            result = [None, None, None]
        return result

    def _read_iip(self, dcmFile):
        """Returns the Image Position Patient without checks, fast but unsafe

        Args:
            dcmFile (pydicom.dataset.FileDataset): Dicom file

        Returns:
            list: Three item list of Image Position Patient

        Info:
            (0020, 0032) Image Position (Patient) Hexcode for IIP (Faster access)
        """        
        return dcmFile[0x0020, 0x0032].value

class DcmFilter(DcmReader):
    def __init__(self, path, gauss2dSmoothSigma=3):
        super().__init__(path)
        self.gauss2dSmoothSigma = gauss2dSmoothSigma
        self.filtered = self._smooth_array()

    def _smooth_array(self):
        """Gaussian 2D filter

        Returns:
            np.ndarray: Result from the gaussian filter
        """        
        return gaussian_filter(self.original, sigma=self.gauss2dSmoothSigma)

class DcmRotate(DcmReader):
    def __init__(self, path, angle=180):
        super().__init__(path)
        self.angle = angle
        self._rotate_array()

    def _rotate_array(self):
        """Rotation function, only rotates when it's a multiple of 90 
        """        
        if self.angle in (90, 180, 270):
            self.rotated = rotate(self.original, angle=self.angle)
        else:
            self.rotated = self.original.copy()

def check_ipp(dcm1, dcm2):
    """Check of two 

    Args:
        dcm1 (DcmReader): DcmReader class (Either DcmFilter or DcmRotate are childs of DcmReader)
        dcm2 (DcmReader): DcmReader class (Either DcmFilter or DcmRotate are childs of DcmReader)

    Returns:
        bool: True if IPP is the same, False otherwise
    """    
    if isinstance(dcm1, DcmReader) & isinstance(dcm2, DcmReader):
        return np.all(dcm1.iip == dcm2.iip)
    else:
        print("Not an instance of DcmReader")
        return False

class IncorrectNumberOfImages(Exception):
    """Incorrect Number of Images in folder, should have exactly two .dcm files in it """
    pass

class SameImagePositionPatient(Exception):
    """The DICOM files have the same ImagePositionPatient values"""
    pass

def saveFullDynamicRange(array, fileName):
    """Saves image with Full dynamic Range.
    Since uint16 can't be saved in jpeg

    Args:
        array (np.ndarray): Image array in np.uint16
        fileName (str): Path + fileName of the destination
    """    
    im = img_as_ubyte(array)
    imsave(f"{fileName}", im)


if __name__ == "__main__":
    input_folder = os.path.normpath(sys.argv[1])
    print(f"Reading folder {input_folder} ... ", end="")

    dcmFiles = glob(f"{input_folder}/*.dcm")
    if len(dcmFiles) != 2:
        print("Incorrect number of images. Aborting.")
        raise IncorrectNumberOfImages()

    # Reading files in folder as dcm1 and dcm2
    dcm1, dcm2 = DcmFilter(dcmFiles[0], gauss2dSmoothSigma=3), DcmFilter(dcmFiles[1], gauss2dSmoothSigma=3)

    # Check if ImagePositionPatient values are the same for both images, raise an error if needed.
    if check_ipp(dcm1, dcm2):
        print("The DICOM files appear to be the same. Aborting.")
        raise SameImagePositionPatient

    # Voxelwise Substraction Operations
    # Unfiltered residue
    unfiltered_residue = dcm1.original - dcm2.original

    # Filtered residue
    filtered_residue = dcm1.filtered - dcm2.filtered

    # Check if residues folder exists, if not then it's created
    residues_folder = f"{input_folder}/residues"
    if not os.path.isdir(residues_folder):
        os.mkdir(residues_folder)

    saveFullDynamicRange(unfiltered_residue, f"{residues_folder}/unfiltered_residue.jpg")
    saveFullDynamicRange(filtered_residue, f"{residues_folder}/filtered_residue.jpg")


    print("Done :)")