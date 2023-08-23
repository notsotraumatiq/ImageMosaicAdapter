import os
from PIL import Image
import pydicom
from pydicom import Dataset
from pydicom.uid import generate_uid

# Input and ouput directories
input_dir = './images/mosaics'
output_dir = './images/dicom-mosaics'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

series_number = 0

# Loop through PNG images in the input directory
for png_filename in os.listdir(input_dir):
    if png_filename.endswith('.png'):
        # Directory containing the PNG image
        png_path = os.path.join(input_dir, png_filename)

        # Read the PNG image
        png_image = Image.open(png_path)

        # Increment Series Number
        series_number += 1

        # Create a DICOM dataset
        # Ideally, more metadata would be fed in here while converting images
        ds = Dataset()
        ds.PatientName = 'John Doe'
        ds.PatientID = '12345'
        ds.StudyInstanceUID = generate_uid()
        ds.StudyDescription = 'Cells Mosaic'
        ds.SeriesInstanceUID = generate_uid()
        ds.SeriesNumber = series_number
        ds.SOPInstanceUID = generate_uid()
        ds.Modality = 'OT' # Other
        ds.Rows = png_image.height
        ds.Columns = png_image.width

        # Set endianness and VR encoding
        ds.is_little_endian = True
        ds.is_implicit_VR = True

        # Convert PIL image to bytes and store as Pixel Data
        ds.PixelData = png_image.tobytes()

        # Save DICOM file
        dicom_filename = os.path.splitext(png_filename)[0] + '.dcm'
        dicom_path = os.path.join(output_dir, dicom_filename)
        ds.save_as(dicom_path)

        print(f"Converted {png_filename} to {dicom_filename}")