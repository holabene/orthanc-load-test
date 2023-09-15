from locust import HttpUser, task, between
import random

class ApiReadTest(HttpUser):
    wait_time = between(1, 5)

    @task
    def get_system(self):
        self.client.get("/system")

    @task
    def open_studies(self):
        study_ids = self.client.get("/studies").json()
        # pick a random study id from the list
        study_id = random.choice(study_ids)

        study = self.client.get(f"/studies/{study_id}", name="/studies/{study_id}").json()
        series_ids = study["Series"]

        for series_id in series_ids:
            series = self.client.get(f"/series/{series_id}", name="/series/{series_id}").json()

            for instance_id in series["Instances"]:
                self.client.get(f"/instances/{instance_id}", name="/instances/{instance_id}")


class DownloadTest(HttpUser):
    wait_time = between(1, 5)

    @task
    def preview_image(self):
        instance_ids = self.client.get("/instances").json()
        # pick a random instance_id from the list
        instance_id = random.choice(instance_ids)
        self.client.get(f"/instances/{instance_id}/preview", name="/instances/{instance_id}/preview")

    @task
    def download_image(self):
        instance_ids = self.client.get("/instances").json()
        # pick a random instance_id from the list
        instance_id = random.choice(instance_ids)
        self.client.get(f"/instances/{instance_id}/file", name="/instances/{instance_id}/file")

    @task
    def download_series(self):
        series_ids = self.client.get("/series").json()
        # pick a random series_id from the list
        series_id = random.choice(series_ids)
        self.client.get(f"/series/{series_id}/archive", name="/series/{series_id}/archive")

    @task
    def download_study(self):
        study_ids = self.client.get("/studies").json()
        # pick a random study_id from the list
        study_id = random.choice(study_ids)
        self.client.get(f"/studies/{study_id}/archive", name="/studies/{study_id}/archive")

    @task
    def download_patient(self):
        patient_ids = self.client.get("/patients").json()
        # pick a random patient_id from the list
        patient_id = random.choice(patient_ids)
        self.client.get(f"/patients/{patient_id}/archive", name="/patients/{patient_id}/archive")


class AnonymizeTest(HttpUser):
    wait_time = between(1, 5)

    @task
    def anonymize_studies(self):
        study_ids = self.client.get("/studies").json()
        # pick a random study id from the list
        study_id = random.choice(study_ids)
        self.client.post(f"/studies/{study_id}/anonymize", json={ "Asynchronous": True }, name="/studies/{study_id}/anonymize")
