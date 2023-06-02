Orthanc Load Test
=================

This is a load test for Orthanc DICOM server. It is based on [Locust](http://locust.io/).

## Installation

```bash
$ brew install python3
$ brew install locust
```

Refer to [Locust Documentation](http://docs.locust.io/en/latest/installation.html) for more details.

## Usage

```bash
$ # bring up the local services in docker-compose.yml
$ docker compose up -d
$ # run the load test
$ locust -f locustfile.py --host=http://orthanc:orthanc@localhost:8042
```

Then open http://localhost:8089/ in your browser and start a test.

## Screenshots

![Screenshot](docs/statistics.png)

![Screenshot](docs/charts.png)


