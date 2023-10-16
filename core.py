from locust import HttpUser, task, between, events

import os
import logging
import zipfile

logger = logging.getLogger(__name__)


class CoreTest(HttpUser):
    wait_time = between(10, 20)

    @task
    def upload_anonymize(self):
        # get all the files in .data/test_data
        files = os.listdir(".data/test_data")

        for file in files:
            # read the zip file, iterate files in zip, and post each file to /instances
            # Open the ZIP file in read mode
            with zipfile.ZipFile(f".data/test_data/{file}", 'r') as zip_file:
                # Iterate over the extracted files
                for extracted_file in zip_file.namelist():
                    # Read the file
                    with zip_file.open(extracted_file, 'r') as dicom_file:
                        # log the file name
                        logger.info(f"Uploading file: {extracted_file}")

                        # Post the file to /instances
                        res = self.client.post("/instances", data=dicom_file, headers={
                            "Content-Type": "application/dicom"
                        }).json()

                        # log the response
                        logger.info(f"Uploaded file {extracted_file}: {res}")



