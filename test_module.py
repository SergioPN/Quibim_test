from dicomhandling import *

if __name__ == "__main__":
    sample1 = "dicom_images/IM-0001-0035-0001.dcm"
    sample2 = "dicom_images/IM-0001-0086-0001.dcm"

    filtered1 = DcmFilter(sample1, gauss2dSmoothSigma=5)
    rotated1 = DcmRotate(sample1, angle=90)
    rotated1 = DcmRotate(sample1)
    filtered2 = DcmFilter(sample2, gauss2dSmoothSigma=5)
    rotated2 = DcmRotate(sample2, angle=90)

    assert check_ipp(filtered1, rotated1) == check_ipp(rotated1, filtered1) == True
    assert check_ipp(filtered2, rotated2) == check_ipp(rotated2, filtered2) == True
    assert check_ipp(filtered1, rotated2) == check_ipp(rotated2, filtered1) == False
    assert check_ipp(filtered2, rotated1) == check_ipp(rotated1, filtered2) == False

