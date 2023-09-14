from locust import HttpUser, task, between


class ApiReadTest(HttpUser):
    wait_time = between(1, 5)

    @task
    def get_system(self):
        self.client.get("/system")

    @task
    def open_studies(self):
        study_ids = self.client.get("/studies", name="/studies")

        for study_id in study_ids.json():
            study = self.client.get(f"/studies/{study_id}", name="/studies/{study_id}")
            series_ids = study.json()["Series"]

            for series_id in series_ids:
                series = self.client.get(f"/series/{series_id}", name="/series/{series_id}")

                for instance_id in series.json()["Instances"]:
                    self.client.get(f"/instances/{instance_id}", name="/instances/{instance_id}")


class DownloadTest(HttpUser):
    wait_time = between(1, 5)

    @task
    def preview_image(self):
        instance_ids = self.client.get("/instances")

        for instance_id in instance_ids.json():
            self.client.get(f"/instances/{instance_id}/preview", name="/instances/{instance_id}/preview")

    @task
    def download_image(self):
        instance_ids = self.client.get("/instances")

        for instance_id in instance_ids.json():
            self.client.get(f"/instances/{instance_id}/file", name="/instances/{instance_id}/file")

    @task
    def download_series(self):
        series_ids = self.client.get("/series")

        for series_id in series_ids.json():
            self.client.get(f"/series/{series_id}/archive", name="/series/{series_id}/archive")

    @task
    def download_study(self):
        study_ids = self.client.get("/studies")

        for study_id in study_ids.json():
            self.client.get(f"/studies/{study_id}/archive", name="/studies/{study_id}/archive")

    @task
    def download_patient(self):
        patient_ids = self.client.get("/patients")

        for patient_id in patient_ids.json():
            self.client.get(f"/patients/{patient_id}/archive", name="/patients/{patient_id}/archive")


class AnonymizeTest(HttpUser):
    wait_time = between(1, 5)

    @task
    def anonymize_studies(self):
        study_ids = self.client.get("/studies", name="/studies")

        for study_id in study_ids.json():
            self.client.post(f"/studies/{study_id}/anonymize", json={ "Asynchronous": True }, name="/studies/{study_id}/anonymize")
