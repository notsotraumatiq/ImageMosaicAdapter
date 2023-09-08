import os
import sys
from PIL import Image
import pydicom
import numpy as np
from pydicom.uid import generate_uid
import string
import random
import tempfile
from splitMosaic import split_image

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

    # Generate uuids
    sopInstanceUID = generate_uid(prefix=prefix)
    studyInstanceUID = generate_uid(prefix=prefix)
    seriesInstanceUID = generate_uid(prefix=prefix)
    dimensionOrgUID = generate_uid(prefix=prefix)

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
    ds.StudyInstanceUID = studyInstanceUID
    ds.SeriesInstanceUID = seriesInstanceUID
    ds.StudyID = studyId
    ds.SeriesNumber = None # ?

    # Dimension Data
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
    print(f"width: {png_image.width}, height: {png_image.height}")
    ds.Rows = png_image.height
    ds.Columns = png_image.width
    ds.SamplesPerPixel = 3
    ds.PhotometricInterpretation = 'RGB'
    ds.PlanarConfiguration = 0
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0

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

    np_image = np.array(png_image.getdata(), dtype=np.uint16)[:,:3]
    # img_array = np.array(png_image)
    # ds.PixelData = np_image.tobytes()

    # For each image, create 3 separate resolutions:
    # resolutions = [
    #     {
    #         'name': 'highRes',
    #         'numberOfFrames': 182,
    #         'width_factor': 12,
    #         'height_factor': 12,
    #         'pixelSpacing': [0.0009706, 0.0009701]
    #     },
    #     {
    #         'name': 'medRes',
    #         'numberOfFrames': 49,
    #         'width_factor': 6,
    #         'height_factor': 6,
    #         'pixelSpacing': [0.0019412, 0.0019403]
    #     },
    #     {
    #         'name': 'lowRes',
    #         'numberOfFrames': 9,
    #         'width_factor': 3,
    #         'height_factor': 3,
    #         'pixelSpacing': [0.0038824, 0.0038806]
    #     }
    # ]
    # for res in resolutions:

    #     # Output path
    #     base_name, extension = os.path.splitext(filename)
    #     output_filename = f"{base_name}{suffix}_{res['name']}.dicom"
    #     output_path = os.path.join(output_dir, output_filename)

    #     total_width = png_image.width * res['width_factor']
    #     total_height = png_image.height * res['height_factor']
        
    #     numberOfFrames = res['numberOfFrames']
    #     ds.NumberOfFrames = numberOfFrames

    #     resized_img = np.resize(np_image, (total_height, total_width, 3))
    #     pixel_data = resized_img.tobytes()

    #     frame_width = png_image.width
    #     frame_height = png_image.height
    #     frame_pixel_size = len(pixel_data) // numberOfFrames
    #     pixelSpacing = res['pixelSpacing']

    #     ds.TotalPixelMatrixColumns = total_width
    #     ds.TotalPixelMatrixRows = total_height

    #     pixel_data_sequence = pydicom.Sequence()

        # frame width is 5x5 image minus borders (6)
        # frame width: (width - 6) / 5

        # for frame_number in range(numberOfFrames):
        #     start_index = frame_number * frame_pixel_size
        #     end_index = start_index + frame_pixel_size
        #     frame_pixel_data = pixel_data[start_index:end_index]

        #     frame_ds = pydicom.Dataset()
        #     frame_ds.PixelData = frame_pixel_data
        #     frame_ds.InstanceNumber = frame_number + 1

        #     frame_ds.Rows = frame_height
        #     frame_ds.Columns = frame_width

        #     pixel_data_sequence.append(frame_ds)

        # ds.PixelData = pixel_data_sequence

        # ds.PixelData = np.tile(pixel_data, int(numberOfFrames))
        ds.PixelData = np_image.tobytes()


        pixelMatrixOrigin = pydicom.dataset.Dataset()
        pixelMatrixOrigin.XOffsetInSlideCoordinateSystem = '0.0'
        pixelMatrixOrigin.YOffsetInSlideCoordinateSystem = '0.0'
        ds.TotalPixelMatrixOriginSequence = pydicom.sequence.Sequence([pixelMatrixOrigin])

        pixelMeasures = pydicom.dataset.Dataset()
        pixelMeasures.SliceThickness = '0.0'
        pixelMeasures.PixelSpacing = pixelSpacing
        pmSequence = pydicom.sequence.Sequence([pixelMeasures])

        wsmImageFrameType = pydicom.dataset.Dataset()
        wsmImageFrameType.FrameType = ['DERIVED', 'PRIMARY', 'VOLUME', 'NONE']
        wsmiftSequence = pydicom.sequence.Sequence([wsmImageFrameType])

        sharedFuncGroup = pydicom.dataset.Dataset()
        sharedFuncGroup.PixelMeasuresSequence = pmSequence
        sharedFuncGroup.WholeSlideMicroscopyImageFrameTypeSequence = wsmiftSequence
        sfgSequence = pydicom.sequence.Sequence([sharedFuncGroup])

        ds.SharedFunctionalGroupsSequence = sfgSequence

        # Save Dicom Image
        ds.save_as(output_path, write_like_original=False)

        print(f"Modified version of {filename} stored as {output_path}")