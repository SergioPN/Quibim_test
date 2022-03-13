# Prueba Quibim 

## Dicom Handler

Module developed using Python 3.9.1 for handling dicom images with one channel

```bash
python -m dicomhandling folder_name
```

## Docker version

To build and run the docker just use the following with the proper folder path/name.

```bash
docker build -t dicom .

docker run -v /full/path/folder_name:/dicom_images dicom
```