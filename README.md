Orthanc Load Test
=================

This is a load test for Orthanc DICOM server. It is based on [Locust](http://locust.io/).

## Installation

```bash
$ brew install poetry # or pip install poetry
$ poetry install
```

Refer to [Locust Documentation](http://docs.locust.io/en/latest/installation.html) for more details.

## Usage

> **Warning**: The load test will create a lot of DICOM instances in the Orthanc server, and also perform delete operations on created instances.
>
> **It is recommended to use a separate Orthanc server for testing and not the production one.**
>
> Also recommended to upload a few DICOM studies to the Orthanc server before running the load test.

```bash
$ # bring up the local services in docker-compose.yml
$ docker compose up -d
$ # run the load test
$ poetry run locust --host=http://orthanc:orthanc@localhost:8042
```

Then open http://localhost:8089/ in your browser and start a test.

To run headless, in this case, the test will run for 1 minute with 100 users and 10 users spawned per second:

```bash
$ poetry run locust --host=http://orthanc:orthanc@localhost:8042 --headless -u 100 -r 10 -t 1m
```

There is `locust-plugins` package available, which provides some useful features, such as limit iterations to run 1 task once:

```bash
$ poetry run locust --host=http://orthanc:orthanc@localhost:8042 --headless -u 1 -i 1
```


## Screenshots

![Screenshot](docs/statistics.png)

![Screenshot](docs/charts.png)


