from locust import HttpUser, task, between


class ApiReadTest(HttpUser):
    wait_time = between(1, 5)

    @task
    def get_system(self):
        self.client.get("/system")

    @task
    def open_studies(self):
        study_ids = self.client.get("/studies")

        for study_id in study_ids.json():
            study = self.client.get(f"/studies/{study_id}")
            series_ids = study.json()["Series"]

            for series_id in series_ids:
                series = self.client.get(f"/series/{series_id}")

                for instance_id in series.json()["Instances"]:
                    self.client.get(f"/instances/{instance_id}")
