# A module for extracting and storing dicom images from the Slim demo webserver
from dicomweb_client.api import DICOMwebClient
from pydicom.dataset import Dataset
import pydicom
from pprint import pprint
import os
from tqdm import tqdm

output_dir = './images/slim-demo-dicoms'

# Make output directory if not exists:
os.makedirs(output_dir, exist_ok=True)

client = DICOMwebClient(url='https://idc-external-006.uc.r.appspot.com/dcm4chee-arc/aets/DCM4CHEE/rs')

# Search for instances
instances = client.search_for_instances()

# Initialize counters for successful downloads, and server errors
successful_downloads = 0
server_errors = 0

for instance in tqdm(instances, desc="Downloading DICOM instances", unit="instance"):
    study_instance_uid = instance['0020000D']['Value'][0]
    series_instance_uid = instance['0020000E']['Value'][0]
    sop_instance_uid = instance['00080018']['Value'][0]

    try:
        dicom_obj = client.retrieve_instance(
            study_instance_uid=study_instance_uid,
            series_instance_uid=series_instance_uid,
            sop_instance_uid=sop_instance_uid
        )
    except Exception as error:
        # print(f"Unable to retrieve instance {sop_instance_uid}", error)
        server_errors += 1
        continue

    # Create a file name and store in output directory
    modality = dicom_obj.get("Modality","NA")
    seriesInstanceUID = dicom_obj.get("SeriesInstanceUID","NA")
    instanceNumber = str(dicom_obj.get("InstanceNumber","0"))
    fileName = modality + "." + seriesInstanceUID + "." + instanceNumber + ".dcm"
    output_path = os.path.join(output_dir, fileName)
    dicom_obj.save_as(output_path)

    successful_downloads += 1
    # print(f"{fileName} created and stored at {output_dir}")

print("Download completed.")
print(f"Successful downloads: {successful_downloads}")
print(f"Server errors: {server_errors}")
