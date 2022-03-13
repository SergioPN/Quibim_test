FROM ubuntu:20.04

# Installing packages to read dicom and handling all the features
WORKDIR /

# Install dependencies
RUN apt-get update && apt-get install -y python3-pip

# Copy files and install libraries
COPY requirements.txt requirements.txt
COPY dicomhandling.py dicomhandling.py
RUN pip install -r requirements.txt

# Setting the entry point
ENTRYPOINT ["python3", "-m", "dicomhandling", "dicom_images"]

# docker build -t dicom .
# docker run -v /full/path/dicom_images:/dicom_images dicom