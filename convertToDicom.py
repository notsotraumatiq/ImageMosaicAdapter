import os
import sys
from PIL import Image
import pydicom
import numpy as np
from pydicom.uid import generate_uid
import string
import random

# Add an optional suffix to the output file name for writing multiple files
# Usage: python3 convertToDicom.py output_suffix
suffix = ''
if len(sys.argv) == 2:
    suffix = sys.argv[1]

# For now, just take a pre-converted dicom,
# And experiment with changing certain settings until viewable in viewer
input_dir = './images/dicom-trials/input'
output_dir = './images/dicom-trials/output'

# Create ouput directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Loop through input directory images
for filename in os.listdir(input_dir):
    image_path = os.path.join(input_dir, filename)

    # If the input file is a dicom image...
    if filename.endswith((".dcm", ".dicom")):
        try:
            ds = pydicom.dcmread(image_path)
        except Exception as error:
            print(f"Could not read dicom input file", error)
            sys.exit(1)

    # If the input file is a png image...
    elif filename.endswith(".png"):
        try:
            png_image = Image.open(image_path)
        except Exception as error:
            print(f"Could not read png input file", error)
            sys.exit(1)
        
        ds = pydicom.dataset.Dataset()
        ds.file_meta = pydicom.dataset.Dataset()
        ds.SamplesPerPixel = 3
        ds.PhotometricInterpretation = 'RGB'
        ds.PlanarConfiguration = 0
        ds.NumberOfFrames = '1'
        ds.Rows = png_image.height
        ds.Columns = png_image.width
        ds.BitsAllocated = 8
        ds.BitsStored = 8
        ds.HighBit = 7
        ds.PixelRepresentation = 0
        ds.PixelData = png_image.tobytes()

        ds.is_little_endian = True
        ds.is_implicit_VR = False


    ###################################################################
    ####    Hardcoding values taken from an example-dicom image    ####
    ###################################################################

    ds.file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.77.1.6' # VL Whole Slide Microscopy Image Storage

    # Implementation Prefix based off dcm4chee-arc docs
    implementationClassUID = '1.2.40.13.1.3'
    prefix = implementationClassUID + '.'

    # Create a random studyId of 7 alphanumeric digits
    # This will eventually be changed to reflect an actual studyId
    studyId = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

    # Generate uid for SOPInstanceUID
    sopInstanceUID = generate_uid(prefix=prefix)

    ds.file_meta.MediaStorageSOPInstanceUID = sopInstanceUID
    ds.file_meta.ImplementationClassUID = implementationClassUID # from dcm4chee-arc docs
    ds.file_meta.ImplementationVersionName = 'dcm4che-5.xx.yy' # from dcm4chee-arc docs
    ds.file_meta.SourceApplicationEntityTitle = 'OURAETITLE'

    ds.ImageType = ['DERIVED', 'PRIMARY', 'VOLUME', 'NONE']
    ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.77.1.6' # VL Whole Slide Microscopy Image Storage
    ds.SOPInstanceUID = sopInstanceUID
    ds.AccessionNumber = studyId
    ds.Modality = 'SM' # Slide Microscopy

    # Study / Series Information
    ds.StudyInstanceUID = generate_uid(prefix=prefix)
    ds.SeriesInstanceUID = generate_uid(prefix=prefix)
    ds.StudyID = studyId
    ds.SeriesNumber = '1'
    ds.InstanceNumber = '1'

    # Dimension Data
    dimensionOrgUID = generate_uid(prefix=prefix)
    dimensionOrg = pydicom.dataset.Dataset()
    dimensionOrg.DimensionOrganizationUID = dimensionOrgUID
    doSequence = pydicom.sequence.Sequence([dimensionOrg])
    ds.DimensionOrganizationSequence = doSequence

    dimensionIndexRow = pydicom.dataset.Dataset()
    dimensionIndexRow.DimensionOrganizationUID = dimensionOrgUID
    dimensionIndexRow.DimensionIndexPointer = (0x0048, 0x021f)
    dimensionIndexRow.FunctionalGroupPointer = (0x0048, 0x021a)
    dimensionIndexRow.DimensionDescriptionLabel = 'Row Position'

    dimensionIndexColumn = pydicom.dataset.Dataset()
    dimensionIndexColumn.DimensionOrganizationUID = dimensionOrgUID
    dimensionIndexColumn.DimensionIndexPointer = (0x0048, 0x021e)
    dimensionIndexColumn.FunctionalGroupPointer = (0x0048, 0x021a)
    dimensionIndexColumn.DimensionDescriptionLabel = 'Column Position'

    diSequence = pydicom.sequence.Sequence([dimensionIndexRow, dimensionIndexColumn])
    ds.DimensionIndexSequence = diSequence

    ds.DimensionOrganizationType = 'TILED_FULL'

    # Image Data
    ds.TotalPixelMatrixColumns = 656*4
    ds.TotalPixelMatrixRows = 656*4

    pixelMatrixOrigin = pydicom.dataset.Dataset()
    pixelMatrixOrigin.XOffsetInSlideCoordinateSystem = '0.0'
    pixelMatrixOrigin.YOffsetInSlideCoordinateSystem = '0.0'
    ds.TotalPixelMatrixOriginSequence = pydicom.sequence.Sequence([pixelMatrixOrigin])

    ds.ImageOrientationSlide = [0, -1, 0, -1, 0, 0] # necessary

    # Optical Path Data
    illumTypeCode = pydicom.dataset.Dataset()
    illumTypeCode.CodeValue = '111744'
    illumTypeCode.CodingSchemeDesignator = 'DCM'
    illumTypeCode.CodeMeaning = 'Brightfield illumination'
    itcSequence = pydicom.sequence.Sequence([illumTypeCode])

    illumColorCode = pydicom.dataset.Dataset()
    illumColorCode.CodeValue = 'R-102C0'
    illumColorCode.CodingSchemeDesignator = 'SRT'
    illumColorCode.CodeMeaning = 'Full Spectrum'
    iccSequence = pydicom.sequence.Sequence([illumColorCode])

    opticalPath = pydicom.dataset.Dataset()
    opticalPath.IlluminationTypeCodeSequence = itcSequence
    # opticalPath.ICCProfile - Array of 141922 elements
    opticalPath.OpticalPathIdentifier = '1'
    opticalPath.IlluminationColorCodeSequence = iccSequence
    ds.OpticalPathSequence = pydicom.sequence.Sequence([opticalPath])

    ds.NumberOfOpticalPaths = 1
    ds.TotalPixelMatrixFocalPlanes = 1

    pixelMeasures = pydicom.dataset.Dataset()
    pixelMeasures.SliceThickness = '0.0'
    pixelMeasures.PixelSpacing = [.008, .008]
    pmSequence = pydicom.sequence.Sequence([pixelMeasures])

    wsmImageFrameType = pydicom.dataset.Dataset()
    wsmImageFrameType.FrameType = ['DERIVED', 'PRIMARY', 'VOLUME', 'NONE']
    wsmiftSequence = pydicom.sequence.Sequence([wsmImageFrameType])

    sharedFuncGroup = pydicom.dataset.Dataset()
    sharedFuncGroup.PixelMeasuresSequence = pmSequence
    sharedFuncGroup.WholeSlideMicroscopyImageFrameTypeSequence = wsmiftSequence
    sfgSequence = pydicom.sequence.Sequence([sharedFuncGroup])

    ds.SharedFunctionalGroupsSequence = sfgSequence

    ###################################################################
    ###################################################################

    # Output the file to the output directory
    base_name, extension = os.path.splitext(filename)
    output_filename = f"{base_name}{suffix}.dicom"
    output_path = os.path.join(output_dir, output_filename)
    ds.save_as(output_path)

    print(f"Modified version of {filename} stored as {output_path}")