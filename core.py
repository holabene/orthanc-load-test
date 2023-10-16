from locust import HttpUser, task, between, events

import os
import logging
import zipfile

logger = logging.getLogger(__name__)
study_ids = {}


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

                        if "ParentStudy" in res.keys() and file not in study_ids.keys():
                            # add the study ID to the list
                            study_ids[file] = res["ParentStudy"]


@events.test_start.add_listener
def on_test_start(**kwargs):
    logger.info("Starting test")


@events.test_stop.add_listener
def on_test_stop(**kwargs):
    logger.info("Stopping test")

    # print study_ids
    logger.info(f"Study IDs: {study_ids}")
