import sys
import pydicom

# For accessing pydicom's sample dicom file
# from pydicom.data import get_testdata_file

# Check for correct usage
if len(sys.argv) != 2:
    print(f"Usage: python {sys.argv[0]} path/to/dicom_file.dcm")
    sys.exit(1)

# Read dicom_file_path from command-line argument
dicom_file_path = sys.argv[1] 

# pydicom comes with a small sample dicom file:
# dicom_file_path = get_testdata_file('CT_small.dcm')

try:
    ds = pydicom.dcmread(dicom_file_path)
except:
    print(f"Could not read file at {dicom_file_path}")
    sys.exit(2)

print(ds)

