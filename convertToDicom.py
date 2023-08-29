import os
import sys
from PIL import Image
import pydicom
import numpy as np
from pydicom.uid import generate_uid

# Add an optional suffix to the output file name for writing multiple files
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
    # Read the example DICOM image
    dicom_path = os.path.join(input_dir, filename)
    try:
        ds = pydicom.dcmread(dicom_path)
    except Exception as error:
        print(f"Could not read dicom input file", error)
        sys.exit(1)

    ###################################################################
    ####    Hardcoding values taken from an example-dicom image    ####
    ###################################################################

    ds.file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.77.1.6' # VL Whole Slide Microscopy Image Storage

    # Implementation Prefix based off dcm4chee-arc docs
    implementationClassUID = '1.2.40.13.1.3'
    prefix = implementationClassUID + '.'

    # Generate uid for SOPInstanceUID
    sopInstanceUID = generate_uid(prefix=prefix)

    ds.file_meta.MediaStorageSOPInstanceUID = sopInstanceUID
    ds.file_meta.ImplementationClassUID = implementationClassUID # from dcm4chee-arc docs
    ds.file_meta.ImplementationVersionName = 'dcm4che-5.xx.yy' # from dcm4chee-arc docs
    ds.file_meta.SourceApplicationEntityTitle = 'OURAETITLE'

    ds.ImageType = ['DERIVED', 'PRIMARY', 'VOLUME', 'NONE']
    ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.77.1.6' # VL Whole Slide Microscopy Image Storage
    ds.SOPInstanceUID = sopInstanceUID
    ds.AccessionNumber = 'S07-100'
    ds.Modality = 'SM' # Slide Microscopy

    # Coding Scheme Sequence
    codingSchemeDCM = pydicom.dataset.Dataset()
    codingSchemeDCM.CodingSchemeDesignator = 'DCM'
    codingSchemeDCM.CodingSchemeUID = '1.2.840.10008.2.16.4'
    codingSchemeDCM.CodingSchemeRegistry = 'HL7'
    codingSchemeDCM.CodingSchemeName = 'DICOM Controlled Terminology'

    codingSchemeSRT = pydicom.dataset.Dataset()
    codingSchemeSRT.CodingSchemeDesignator = 'SRT'
    codingSchemeSRT.CodingSchemeUID = '2.16.840.1.113883.6.96'
    codingSchemeSRT.CodingSchemeRegistry = 'HL7'
    codingSchemeSRT.CodingSchemeName = 'SNOMED-CT using SNOMED-RT style values'

    ds.CodingSchemeIdentificationSequence = pydicom.sequence.Sequence([codingSchemeDCM, codingSchemeSRT])

    # Study / Series Information
    ds.StudyInstanceUID = generate_uid(prefix=prefix)
    ds.SeriesInstanceUID = generate_uid(prefix=prefix)
    ds.StudyID = 'S07-100'
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

    ds.BurnedInAnnotation = 'NO'
    ds.RecognizableVisualFeatures = 'NO'
    ds.LossyImageCompression = '00'
    ds.ContainerIdentifier = 'S07-100 A 5 1'

    ds.IssuerOfTheContainerIdentifierSequence = pydicom.sequence.Sequence([])

    containerTypeCode = pydicom.dataset.Dataset()
    containerTypeCode.CodeValue = 'A-0101B'
    containerTypeCode.CodingSchemeDesignator = 'SRT'
    containerTypeCode.CodeMeaning = 'Microscope slide'
    ds.ContainerTypeCodeSequence = pydicom.sequence.Sequence([containerTypeCode])

    ds.AcquisitionContextSequence = pydicom.sequence.Sequence([])

    # Image Data
    ds.ImagedVolumeWidth = 23.0
    ds.ImagedVolumeHeight = 16.45599937438965
    ds.ImagedVolumeDepth = 0.0
    ds.TotalPixelMatrixColumns = 656
    ds.TotalPixelMatrixRows = 656

    pixelMatrixOrigin = pydicom.dataset.Dataset()
    pixelMatrixOrigin.XOffsetInSlideCoordinateSystem = '0.0'
    pixelMatrixOrigin.YOffsetInSlideCoordinateSystem = '0.0'
    ds.TotalPixelMatrixOriginSequence = pydicom.sequence.Sequence([pixelMatrixOrigin])

    ds.SpecimenLabelInImage = 'NO'
    ds.FocusMethod = 'AUTO'
    ds.ExtendedDepthOfField = 'NO'
    ds.RecommendedAbsentPixelCIELabValue = [65535, 0, 0]
    ds.ImageOrientationSlide = [0, -1, 0, -1, 0, 0]

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
    output_filename = f"{base_name}{suffix}{extension}"
    output_path = os.path.join(output_dir, output_filename)
    ds.save_as(output_path)

    print(f"Modified version of {filename} stored as {output_path}")