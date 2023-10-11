import tempfile
import random
import logging
import os

from locust import HttpUser, task, between, events
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import UID, generate_uid
from datetime import datetime

logger = logging.getLogger(__name__)


class ReadTest(HttpUser):
    """
    Test reading data from Orthanc
    """
    wait_time = between(5, 8)

    @task
    def get_system(self):
        system = self.client.get("/system").json()
        logger.info(f"Orthanc version {system['Version']}")

    @task
    def open_studies(self):
        study_ids = self.client.get("/studies").json()
        # pick a random study id from the list
        study_id = random.choice(study_ids)

        study = self.client.get(f"/studies/{study_id}", name="/studies/{study_id}").json()
        logger.info(f"Opened study {study_id}")

        series_ids = study["Series"]

        for series_id in series_ids:
            series = self.client.get(f"/series/{series_id}", name="/series/{series_id}").json()
            logger.info(f"Opened series {series_id}")

            for instance_id in series["Instances"]:
                self.client.get(f"/instances/{instance_id}", name="/instances/{instance_id}")
                logger.info(f"Opened instance {instance_id}")


class DownloadTest(HttpUser):
    """
    Test downloading data from Orthanc
    """
    wait_time = between(5, 8)

    @task
    def preview_image(self):
        instance_ids = self.client.get("/instances").json()
        # pick a random instance_id from the list
        instance_id = random.choice(instance_ids)
        self.client.get(f"/instances/{instance_id}/preview", name="/instances/{instance_id}/preview")
        logger.info(f"Previewed instance {instance_id}")

    @task
    def download_image(self):
        instance_ids = self.client.get("/instances").json()
        # pick a random instance_id from the list
        instance_id = random.choice(instance_ids)
        self.client.get(f"/instances/{instance_id}/file", name="/instances/{instance_id}/file")
        logger.info(f"Downloaded instance {instance_id}")

    @task
    def download_series(self):
        series_ids = self.client.get("/series").json()
        # pick a random series_id from the list
        series_id = random.choice(series_ids)
        self.client.get(f"/series/{series_id}/archive", name="/series/{series_id}/archive")
        logger.info(f"Downloaded series {series_id}")

    @task
    def download_study(self):
        study_ids = self.client.get("/studies").json()
        # pick a random study_id from the list
        study_id = random.choice(study_ids)
        self.client.get(f"/studies/{study_id}/archive", name="/studies/{study_id}/archive")
        logger.info(f"Downloaded study {study_id}")

    @task
    def download_patient(self):
        patient_ids = self.client.get("/patients").json()
        # pick a random patient_id from the list
        patient_id = random.choice(patient_ids)
        self.client.get(f"/patients/{patient_id}/archive", name="/patients/{patient_id}/archive")
        logger.info(f"Downloaded patient {patient_id}")


class AnonymizeTest(HttpUser):
    """
    Test running anonymization jobs in async mode
    """
    wait_time = between(10, 12)

    @task
    def anonymize_studies(self):
        study_ids = self.client.get("/studies").json()
        # pick a random study id from the list
        study_id = random.choice(study_ids)
        job = self.client.post(f"/studies/{study_id}/anonymize", json={"Asynchronous": True},
                               name="/studies/{study_id}/anonymize").json()
        logger.info(f"Anonymization job {job['ID']} started for study {study_id}")


class SlowEndpointTest(HttpUser):
    """
    Test slow endpoints, which requires file reading on the server side
    """
    wait_time = between(10, 12)

    @task
    def simplified_tags(self):
        study_ids = self.client.get("/studies").json()
        # pick a random study_id from the list
        study_id = random.choice(study_ids)
        # get instances from the study
        instances = self.client.get(f"/studies/{study_id}/instances", name="/studies/{study_id}/instances").json()
        # map the instances to a list of instance ids
        instance_ids = list(map(lambda instance: instance["ID"], instances))
        # pick a random instance_id from the list
        instance_id = random.choice(instance_ids)
        self.client.get(f"/instances/{instance_id}/simplified-tags", name="/instances/{instance_id}/simplified-tags")
        logger.info(f"Retrieved simplified tags for instance {instance_id}")

    @task
    def shared_tags(self):
        study_ids = self.client.get("/studies").json()
        # pick a random study_id from the list
        study_id = random.choice(study_ids)
        self.client.get(f"/studies/{study_id}/shared-tags", name="/studies/{study_id}/shared-tags")
        logger.info(f"Retrieved shared tags for study {study_id}")

    @task
    def tools_find(self):
        study_ids = self.client.get("/studies").json()
        # pick a random study_id from the list
        study_id = random.choice(study_ids)

        # get data from the study
        study = self.client.get(f"/studies/{study_id}", name="/studies/{study_id}").json()
        study_instance_uid = study["MainDicomTags"]["StudyInstanceUID"]
        study_date = study["MainDicomTags"]["StudyDate"] if "StudyDate" in study["MainDicomTags"] else None
        patient_id = study["PatientMainDicomTags"]["PatientID"] \
            if "PatientID" in study["PatientMainDicomTags"] else None

        # search for the study
        self.client.post("/tools/find", json={"Level": "Study", "Expand": True, "Query": {
            "StudyInstanceUID": study_instance_uid,
            "StudyDate": study_date,
            "PatientID": patient_id
        }}, name="/tools/find")

        logger.info(f"Searched for study {study_instance_uid}, study date {study_date}, patient ID {patient_id}")


class WriteTest(HttpUser):
    """
    Test writing data to Orthanc
    """
    wait_time = between(10, 12)

    def create_dicom_file(self):
        """
        Create a DICOM file
        Adapted from https://pydicom.github.io/pydicom/stable/auto_examples/input_output/plot_write_dicom.html#sphx-glr-auto-examples-input-output-plot-write-dicom-py
        :return: DICOM file path
        """
        filename = tempfile.NamedTemporaryFile(suffix=".dcm", dir=".data/temp").name

        file_meta = FileMetaDataset()
        file_meta.MediaStorageSOPClassUID = UID('1.2.840.10008.5.1.4.1.1.2')

        ds = FileDataset(filename, {}, file_meta=file_meta, preamble=b"\0" * 128)
        ds.PatientName = "Test^Patient"
        ds.PatientID = datetime.now().strftime('OrthancLoadTest-%Y%m%d-%H%M%S-%f')
        ds.StudyInstanceUID = generate_uid()
        ds.SeriesInstanceUID = generate_uid()
        ds.SOPInstanceUID = generate_uid()
        ds.Modality = "CT"
        ds.is_little_endian = True
        ds.is_implicit_VR = True
        ds.ContentDate = datetime.now().strftime('%Y%m%d')
        ds.ContentTime = datetime.now().strftime('%H%M%S')

        ds.save_as(filename)

        return filename

    def upload_file(self):
        while True:
            filename = self.create_dicom_file()

            with open(filename, "rb") as file:
                upload = self.client.post("/instances", data=file, headers={
                    "Content-Type": "application/dicom"
                }, name="/instances").json()

            # delete the file
            os.remove(filename)

            # break if status is Success
            if upload["Status"] == "Success":
                logger.info(f"Uploaded file {filename} as instance ID {upload['ID']}, "
                            f"ParentSeries {upload['ParentSeries']}, "
                            f"ParentStudy {upload['ParentStudy']}, "
                            f"ParentPatient {upload['ParentPatient']}")

                break

        return upload

    @task
    def upload_and_delete_instance(self):
        upload = self.upload_file()

        # delete the instance
        self.client.delete(f"/instances/{upload['ID']}", name="/instances/{instance_id}")
        logger.info(f"Deleted instance {upload['ID']}")

    @task
    def upload_and_delete_series(self):
        upload = self.upload_file()

        # count the number of instances in the series
        instances = self.client.get(f"/series/{upload['ParentSeries']}/instances",
                                    name="/series/{series_id}/instances").json()

        logger.info(f"Found {len(instances)} instance(s) in series {upload['ParentSeries']}")

        if len(instances) == 1:
            # delete the series
            self.client.delete(f"/series/{upload['ParentSeries']}", name="/series/{series_id}")
            logger.info(f"Deleted series {upload['ParentSeries']}")
        else:
            # delete the instance
            self.client.delete(f"/instances/{upload['ID']}", name="/instances/{instance_id}")
            logger.info(f"Deleted instance {upload['ID']}")

    @task
    def upload_and_delete_study(self):
        upload = self.upload_file()

        # count the number of instances in the study
        instances = self.client.get(f"/studies/{upload['ParentStudy']}/instances",
                                    name="/studies/{study_id}/instances").json()

        logger.info(f"Found {len(instances)} instance(s) in study {upload['ParentStudy']}")

        if len(instances) == 1:
            # delete the study
            self.client.delete(f"/studies/{upload['ParentStudy']}", name="/studies/{study_id}")
            logger.info(f"Deleted study {upload['ParentStudy']}")
        else:
            # delete the instance
            self.client.delete(f"/instances/{upload['ID']}", name="/instances/{instance_id}")
            logger.info(f"Deleted instance {upload['ID']}")

    @task
    def upload_and_delete_patient(self):
        upload = self.upload_file()

        # count the number of instances in the patient
        instances = self.client.get(f"/patients/{upload['ParentPatient']}/instances",
                                    name="/patients/{patient_id}/instances").json()

        logger.info(f"Found {len(instances)} instance(s) in patient {upload['ParentPatient']}")

        if len(instances) == 1:
            # delete the patient
            self.client.delete(f"/patients/{upload['ParentPatient']}", name="/patients/{patient_id}")
            logger.info(f"Deleted patient {upload['ParentPatient']}")
        else:
            # delete the instance
            self.client.delete(f"/instances/{upload['ID']}", name="/instances/{instance_id}")
            logger.info(f"Deleted instance {upload['ID']}")


@events.test_start.add_listener
def on_test_start(**kwargs):
    # print current time in UTC
    logger.info(f"Test started at {datetime.utcnow()}")

    # create temp folder if not exists
    if not os.path.exists(".data/temp"):
        os.makedirs(".data/temp")

    # clean up temp files
    for root, dirs, files in os.walk(".data/temp"):
        for file in files:
            os.remove(os.path.join(root, file))


@events.test_stop.add_listener
def on_test_stop(**kwargs):
    # print current time in UTC
    logger.info(f"Test stopped at {datetime.utcnow()}")

    # clean up temp files
    for root, dirs, files in os.walk(".data/temp"):
        for file in files:
            os.remove(os.path.join(root, file))
