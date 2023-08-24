# It appears that currently the origin server may not support deletion or
# neccessary permissions must be granted

from dicomweb_client.api import DICOMwebClient

server_url = 'http://localhost:8008/dcm4chee-arc/aets/DCM4CHEE/rs'

client = DICOMwebClient(server_url)

# Perform QIDO-RS query to retrieve instances
response = client.search_for_instances()

# Loop through the response and delete each instance
for instance in response:
    study_instance_uid = instance['0020000D']['Value'][0]
    series_instance_uid = instance['0020000E']['Value'][0]
    sop_instance_uid = instance['00080018']['Value'][0]

    client.delete_instance(study_instance_uid, series_instance_uid, sop_instance_uid)
    print(f"Deleted instance with SOP Instance UID: {sop_instance_uid}")
