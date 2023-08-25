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

    # If there is no Modality attribute, add it
    if 'Modality' not in ds:
        ds.Modality = 'SM' # Slide Microscopy - necessary for Slim
    
    # Output the file to the output directory
    output_path = os.path.join(output_dir, filename)
    ds.save_as(output_path)

    print(f"Modified version of {filename} stored in {output_dir}")


# # Loop through PNG images in the png_dir
# for png_filename in os.listdir(png_dir):
#     # Read the example DICOM image
#     ds = pydicom.Dataset()

#     if png_filename.endswith('.png'):
#         # Read the png image
#         png_path = os.path.join(png_dir, png_filename)
#         png_image = Image.open(png_path)

#         ds.Rows = png_image.height
#         ds.Columns = png_image.width
#         ds.BitsStored = 8
#         ds.BitsAllocated = 8
#         ds.HighBit = 7
#         ds.PixelRepresentation = 0
#         np_image = np.array(png_image.getdata(), dtype=np.uint8)[:,:3]
#         ds.PhotometricInterpretation = "RGB"
#         ds.SamplesPerPixel = 3
#         ds.PixelData = np_image.tobytes()
        
#         ds.is_little_endian = True
#         ds.is_implicit_VR = False

#         dicom_filename = os.path.splitext(png_filename)[0] + '.dcm'
#         dicom_path = os.path.join(output_dir, dicom_filename)
#         ds.save_as(dicom_path)
        
#         print(f"Converted {png_filename} to {dicom_filename}")