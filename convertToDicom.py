import os
import sys
from PIL import Image
import pydicom
import numpy as np

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
    except:
        print(f"Could not read dicom input file")
        sys.exit(1)

    ###################################################################
    ####    Hardcoding values taken from an example-dicom image    ####
    ###################################################################

    ds.file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.77.1.6'
    ds.file_meta.MediaStorageSOPInstanceUID = '1.3.6.1.4.1.5962.99.1.3827483890.1961511620.1550015743218.27.0'
    ds.file_meta.ImplementationClassUID = '1.3.6.1.4.1.5962.99.2'
    ds.file_meta.ImplementationVersionName = 'PIXELMEDJAVA001'
    ds.file_meta.SourceApplicationEntityTitle = 'OURAETITLE'

    ds.ImageType = ['DERIVED', 'PRIMARY', 'VOLUME', 'NONE']
    ds.InstanceCreationDate = '20190212'
    ds.InstanceCreationTime = '191333.182'
    ds.InstanceCreatorUID = '1.3.6.1.4.1.5962.99.3'
    ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.77.1.6' # VL Whole Slide Microscopy Image Storage
    ds.SOPInstanceUID = '1.3.6.1.4.1.5962.99.1.3827483890.1961511620.1550015743218.27.0'
    ds.StudyDate = '20091229'
    ds.SeriesDate = '20091229'
    ds.AcquisitionDate = '20091229'
    ds.AcquisitionDateTime = '20091229095915'
    ds.StudyTime = '095915'
    ds.SeriesTime = '095915'
    ds.AcquisitionTime = '095915'
    ds.AccessionNumber = 'S07-100'
    ds.Modality = 'SM' # Slide Microscopy
    ds.Manufacturer = 'Aperio'
    ds.ReferringPhysicianName = '^^^^'

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
    
    ds.TimezoneOffsetFromUTC = '-0500'
    ds.ManufacturerModelName = 'com.pixelmed.convert.TIFFToDicom'
    ds.VolumetricProperties = 'VOLUME'

    # Patient Information
    ds.PatientName = 'PixelMed^AperioCMU-1'
    ds.PatientID = 'PX7832548325932'
    ds.PatientBirthDate = ''
    ds.PatientSex = ''

    ds.DeviceSerialNumber = '1a0972e83993e25f:74ea4ac4:168e42344f2:-7fe2'
    ds.SoftwareVersions = 'Tue Feb 12 18:10:22 EST 2019'
    ds.ContentQualification = 'RESEARCH'

    # Contributing Equipment Sequence
    contributingEquipment = pydicom.dataset.Dataset()
    contributingEquipment.Manufacturer = 'PixelMed'
    contributingEquipment.InstitutionName = 'PixelMed'
    contributingEquipment.InstitutionAddress = 'Bangor, PA'
    contributingEquipment.ManufacturerModelName = 'com.pixelmed.apps.SetCharacteristicsFromSummary'
    contributingEquipment.SoftwareVersions = 'Vers. Tue Feb 12 18:10:22 EST 2019'
    contributingEquipment.ContributionDateTime = '20190212191333.186-0500'
    contributingEquipment.ContributionDescription = 'Set characteristics from summary'
    ceSequence = pydicom.sequence.Sequence([contributingEquipment])

    purposeOfReferenceCode = pydicom.dataset.Dataset()
    purposeOfReferenceCode.CodeValue = '109103'
    purposeOfReferenceCode.CodingSchemeDesignator = 'DCM'
    purposeOfReferenceCode.CodeMeaning = 'Modifying Equipment'
    porcSequence = pydicom.sequence.Sequence([purposeOfReferenceCode])

    ds.ContributingEquipmentSequence = ceSequence
    ds.ContributingEquipmentSequence[0].PurposeOfReferenceCodeSequence = porcSequence

    # Study / Series Information
    ds.StudyInstanceUID = '1.3.6.1.4.1.5962.99.1.3827483890.1961511620.1550015743218.29.0'
    ds.SeriesInstanceUID = '1.3.6.1.4.1.5962.99.1.3827483890.1961511620.1550015743218.28.0'
    ds.StudyID = 'S07-100' # Necessary
    ds.SeriesNumber = '1'
    ds.InstanceNumber = '1'

    ds.PatientOrientation = ''
    ds.FrameOfReferenceUID = '1.3.6.1.4.1.5962.99.1.3827483890.1961511620.1550015743218.31.0'
    ds.PositionReferenceIndicator = ''

    # Dimension Data
    dimensionOrg = pydicom.dataset.Dataset()
    dimensionOrg.DimensionOrganizationUID = '1.3.6.1.4.1.5962.99.1.3827483890.1961511620.1550015743218.32.0'
    doSequence = pydicom.sequence.Sequence([dimensionOrg])
    ds.DimensionOrganizationSequence = doSequence

    dimensionIndexRow = pydicom.dataset.Dataset()
    dimensionIndexRow.DimensionOrganizationUID = '1.3.6.1.4.1.5962.99.1.3827483890.1961511620.1550015743218.32.0'
    dimensionIndexRow.DimensionIndexPointer = (0x0048, 0x021f)
    dimensionIndexRow.FunctionalGroupPointer = (0x0048, 0x021a)
    dimensionIndexRow.DimensionDescriptionLabel = 'Row Position'

    dimensionIndexColumn = pydicom.dataset.Dataset()
    dimensionIndexColumn.DimensionOrganizationUID = '1.3.6.1.4.1.5962.99.1.3827483890.1961511620.1550015743218.32.0'
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

    ## Specimen Description Info (not yet encoded) ##

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
    output_path = os.path.join(output_dir, filename)
    ds.save_as(output_path)

    print(f"Modified version of {filename} stored in {output_dir}")