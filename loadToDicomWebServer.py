import os
import pydicom
from dicomweb_client.api import DICOMwebClient

# dicom_dir = './images/dicom-images'
dicom_dir = './images/dicom-trials/output'

server_url = 'http://localhost:8008/dcm4chee-arc/aets/DCM4CHEE/rs'
client = DICOMwebClient(server_url)

for filename in os.listdir(dicom_dir):
    dicom_filepath = os.path.join(dicom_dir, filename)
    dataset = pydicom.dcmread(dicom_filepath)
    response = client.store_instances([dataset])
    
    if response.status_code == 200:
        print(f"Stored {filename} successfully.")
    else:
        print(f"Failed to store {filename}. Status code: {response.status_code}")
        print(f"response: {response.data}")