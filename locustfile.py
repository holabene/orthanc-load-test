from locust import HttpUser, task, between, events
import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ApiReadTest(HttpUser):
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
    wait_time = between(10, 12)

    @task
    def anonymize_studies(self):
        study_ids = self.client.get("/studies").json()
        # pick a random study id from the list
        study_id = random.choice(study_ids)
        job = self.client.post(f"/studies/{study_id}/anonymize", json={"Asynchronous": True},
                               name="/studies/{study_id}/anonymize").json()
        logger.info(f"Anonymization job {job['ID']} started for study {study_id}")


@events.test_start.add_listener
def on_test_start(**kwargs):
    # print current time in UTC
    logger.info(f"Test started at {datetime.utcnow()}")


@events.test_stop.add_listener
def on_test_stop(**kwargs):
    # print current time in UTC
    logger.info(f"Test stopped at {datetime.utcnow()}")
