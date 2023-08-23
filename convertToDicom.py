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

# Loop through PNG images in the input directory
for png_filename in os.listdir(input_dir):
    if png_filename.endswith('.png'):
        # Load PNG image
        png_path = os.path.join(input_dir, png_filename)

        # Create a DICOM dataset
        # Ideally, more metadata would be fed in here while converting images
        ds = Dataset()
        ds.SOPInstanceUID = generate_uid()
        ds.Modality = 'OT' # Other
        ds.Rows = ds.Columns = 512 # Replace with actual dimensions

        # Set endianness and VR encoding
        ds.is_little_endian = True
        ds.is_implicit_VR = True

        # Convert PIL image to bytes and store as Pixel Data
        ds.PixelData = open(png_path, 'rb').read()

        # Save DICOM file
        dicom_filename = os.path.splitext(png_filename)[0] + '.dcm'
        dicom_path = os.path.join(output_dir, dicom_filename)
        ds.save_as(dicom_path)

        print(f"Converted {png_filename} to {dicom_filename}")