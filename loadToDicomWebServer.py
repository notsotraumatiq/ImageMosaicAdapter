import os
import requests
import pydicom

server_url = 'http://localhost:8008/dcm4chee-arc/aets/DCM4CHEE/rs/studies/'

dicom_dir = './images/dicom-mosaics'

for filename in os.listdir(dicom_dir):
    dicom_filepath = os.path.join(dicom_dir, filename)
    ds = pydicom.dcmread(dicom_filepath, force=True)

    # print(f"StudyInstanceUID: {ds.StudyInstanceUID}")
    
    # Send POST request to store DICOM instance
    headers = {'Content-Type': 'application/dicom'}
    response = requests.post(server_url + ds.StudyInstanceUID, data=ds.PixelData, headers=headers)
    
    if response.status_code == 200:
        print(f"Stored {filename} successfully.")
    else:
        print(f"Failed to store {filename}. Status code: {response.status_code}")