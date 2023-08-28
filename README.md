# ImageMosaicAdapter
Simple server which provides services to split an image into a mosaic image collection and assemble a set of images into a mosaic

### Developer Instructions
Currently this repository contains both a Node.js project as well as several independent Python scripts.

**Install the Node dependencies:**
```
npm install
```

**Python Virtual Environment:**
* It is recommended to use a Python virtual environment:
```
python -m venv mosaicvenv
```
* Start the virtual environment:
```
source mosaicvenv/bin/activate
```
* To stop your virtual environment:
```
deactivate
```

**Install Python Dependencies:**
```
pip install -r requirements.txt
```

### Starting the Local Webserver
Make sure the *DICOMweb server* is running by following the instructions inside the **Slim** documentation. Spinning up the **Docker** containers will start up the **Slim** application as well as a locally hosted *DICOMweb server*

Make sure your **Docker** engine is running, then inside the **Slim** repository:
```
docker-compose up -d
```

### Converting PNG Images to DICOM
* This approach for converting **PNG** images to **DICOM** is for demo purposes and does not encode the correct metadata onto the images. Instead, the process relies on hard-coding existing metadata from a sample dicom image (currently located at `images/dicom-images/example-dicom.dcm`; tag-list can be found at `dicom-tags/example-dicom.txt`)

1. Convert the **PNG** image to **DICOM** using a [free online png to dicom converter](https://products.groupdocs.app/conversion/png-to-dicom)
2. Store the image in the directory `/images/dicom-trials/input`
3. Encode the necessary **DICOM** tags by running
```
python convertToDicom.py
```
* Note, this step will encode all images in the `images/dicom-trials/input` directory and store the converted **DICOM** images in `images/dicom-trials/output`. Since most of the metadata are hardcoded, likely there will be duplicate IDs resulting in issues storing separate images on the local webserver

### Storing Images on the DICOM Web Server
**Storing Images from the CLI**

Images can be stored using the *dicomweb_client* **Python** package in the CLI:
```
dicomweb_client --url http://localhost:8008/dcm4chee-arc/aets/DCM4CHEE/rs \
store instances \
path/to/dicomfiles/*
```

**Storing Images With the Python Script**

The file `loadToDicomWebServer.py` will store all images located in the `images/dicom-images` directory:
```
python loadToDicomWebServer.py
```
