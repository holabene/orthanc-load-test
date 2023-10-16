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
                        }, name=f"/instances ({file})").json()

                        # log the response
                        logger.info(f"Uploaded file {extracted_file}: {res}")

                        if "ParentStudy" in res.keys() and file not in study_ids.keys():
                            # add the study ID to the list
                            study_ids[file] = res["ParentStudy"]

                study_id = study_ids[file]

                # anonymize the study
                logger.info(f"Anonymizing study {study_id}")
                res = self.client.post(f"/studies/{study_id}/anonymize", json={
                    "Asynchronous": False
                }, name=f"/studies/{study_id}/anonymize ({file})", timeout=25 * 60).json()

                # log the response
                logger.info(f"Anonymized study {study_id}: {res}")

                # result study ID
                anon_study_id = res["ID"]

                # delete the original study
                logger.info(f"Deleting study {study_id}")
                self.client.delete(f"/studies/{study_id}").json()

                # delete the anonymized study
                logger.info(f"Deleting study {anon_study_id}")
                self.client.delete(f"/studies/{anon_study_id}").json()


@events.test_start.add_listener
def on_test_start(**kwargs):
    logger.info("Starting test")


@events.test_stop.add_listener
def on_test_stop(**kwargs):
    logger.info("Stopping test")

    # print study_ids
    logger.info(f"Study IDs: {study_ids}")
