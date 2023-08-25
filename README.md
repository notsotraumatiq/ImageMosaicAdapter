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