import os
import pydicom
from dicomweb_client.api import DICOMwebClient
import sys

if len(sys.argv) == 2: 
    dicom_dir = sys.argv[1]
else:
    print(f"Usage: python {sys.argv[0]} path/to/files-to-load")
    sys.exit(1)

server_url = 'http://localhost:8008/dcm4chee-arc/aets/DCM4CHEE/rs'
client = DICOMwebClient(server_url)

successfully_stored = 0
errors_storing = 0

for filename in os.listdir(dicom_dir):
    dicom_filepath = os.path.join(dicom_dir, filename)
    dataset = pydicom.dcmread(dicom_filepath)
    
    try:
        client.store_instances([dataset])
        successfully_stored += 1
        print(f"Stored {filename} successfully.")
    except Exception as error:
        errors_storing += 1
        print(f"Failed to store {filename}")
        print(error)

print(f"Finished storing dicom files")
print(f"Successfully stored: {successfully_stored}")
print(f"Errors storing: {errors_storing}")