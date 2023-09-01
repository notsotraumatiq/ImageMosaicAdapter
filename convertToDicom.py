import os
import sys
from PIL import Image
import pydicom
import numpy as np
from pydicom.uid import generate_uid
import string
import random
import tempfile

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

    # Output path
    base_name, extension = os.path.splitext(filename)
    output_filename = f"{base_name}{suffix}.dicom"
    output_path = os.path.join(output_dir, output_filename)

    # If the input file is not a png image...
    if not filename.endswith(".png"):
        print(f"{filename} is not a png file")
        continue

    try:
        png_image = Image.open(image_path)
    except Exception as error:
        print(f"Could not read png input file", error)
        sys.exit(1)
        
    # Unique UID prefix
    prefix = '1.2.826.0.1.3680043.10.1286.' # Generated externally
    implementationClassUID = prefix + '1'

    # Create a random studyId of 7 alphanumeric digits
    # This will eventually be changed to reflect an actual studyId
    studyId = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

    # Generate uid for SOPInstanceUID
    sopInstanceUID = generate_uid(prefix=prefix)

    # File Metadata
    file_meta = pydicom.dataset.FileMetaDataset()
    file_meta.FileMetaInformationVersion = b'\x00\x01'
    file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.77.1.6' # VL Whole Slide Microscopy Image Storage
    file_meta.MediaStorageSOPInstanceUID = sopInstanceUID
    file_meta.ImplementationClassUID = implementationClassUID
    file_meta.ImplementationVersionName = '001' # Need to update
    file_meta.SourceApplicationEntityTitle = 'DEXXAE' # Need to update

    tempfilename = tempfile.NamedTemporaryFile(suffix='dicom').name
    ds = pydicom.dataset.FileDataset(tempfilename, {},
                                        file_meta=file_meta, preamble=b"\0" * 128)
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    
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

    np_image = np.array(png_image.getdata(), dtype=np.uint8)[:,:3]
    ds.PixelData = np_image.tobytes()

    ds.TotalPixelMatrixColumns = ds.Columns
    ds.TotalPixelMatrixRows = ds.Rows

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

    ds.save_as(output_path, write_like_original=False)

    print(f"Modified version of {filename} stored as {output_path}")