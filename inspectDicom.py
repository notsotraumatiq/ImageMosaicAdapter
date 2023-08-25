import pydicom

# Load example DICOM file
# dicom_file_path = './images/example-dicom/example-dicom.dcm'
dicom_file_path = './images/mosaic-dicoms/grid0-20pct-black-pad.dcm'
ds = pydicom.dcmread(dicom_file_path)

print(ds)