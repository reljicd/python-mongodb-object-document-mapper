# MongoDB Object Document Mapper

## About 

Object Document Mapper for MongoDB written in Python.

## Prerequisites

\[Optional\] Install virtual environment:

```bash
$> sudo apt install python3-pip
$> pip3 install virtualenv
$> python3 -m virtualenv venv
```

Activate virtual environment:

On macOS and Linux:
```bash
$> source venv/bin/activate
```

On Windows:
```bash
$> .\venv\Scripts\activate
```

\[Optional\] Install dependencies (in a new virtual environment):
```bash
$> pip install -r requirements.txt
```

Add project directory to PYTHONPATH
```bash
$> export PYTHONPATH=$PYTHONPATH:$(pwd)
```

This project also depends on [dict-objectify](https://github.com/reljicd/dict-objectify) project. You will need to clone these projects as well, and add them to your PYTHONPATH. (In PyCharm, you can configure additional project dependencies in: Preferences... > Project:python-mongodb-object-document-mapper > Project Structure > Add Content Root)

## Configuration parameters

Configuration parameters are passed through environment variables.

* **MONGO_HOST** - Mongo host. Defaults to **localhost**.

* **MONGO_PORT** - Mongo port. Defaults to **27017**.

* **MONGO_USERNAME** - Mongo username. Defaults to empty string.

* **MONGO_PASSWORD** - Mongo password. Defaults to empty string.

* **MONGO_USE_SSL** - Should SSL be used. Defaults to **False**.

* **MONGO_CERT_PATH** - Mongo certificate path. Defaults to empty string.

* **MONGO_USE_REPLICA_SET** - Should replica set be used. Defaults to **False**.

* **DB_CONFIGS** - Path of the databases configuration files in yaml format. Defaults to **mongo_odm/config/db_configs**.

## How to run

### Default

```bash
$> python ${SERVICE_NAME} ${METHOD_NAME} [parameters...]
```

#### Helper script

It is possible to run all the above with helper script:

```bash
$> chmod +x scripts/activate_venv_and_run_python.sh
$> scripts/activate_venv_and_run_python.sh ${SERVICE_NAME} ${METHOD_NAME} [parameters...]
```

### Docker

It is possible to run application using Docker:

Build Docker image:
```bash
$> docker build -t mongo_odm -f docker/Dockerfile .
```

Run Docker container:
```bash
$> docker run --rm -t \
        -e MONGO_HOST=${MONGO_HOST} \
        -e MONGO_PORT=${MONGO_PORT} \
        mongo_odm ${SERVICE_NAME} ${METHOD_NAME} [parameters...]
```

#### Docker helper script

It is possible to run all the above with helper script:

```bash
$> chmod +x scripts/run_docker.sh
$> scripts/run_docker.sh ${SERVICE_NAME} ${METHOD_NAME} [parameters...]
```

## Tests

### Default

```bash
$> python -m pytest tests
```

#### Helper script

It is possible to run all the above with helper script:

```bash
$> chmod +x scripts/activate_venv_and_run_python.sh
$> scripts/activate_venv_and_run_python.sh -m pytest tests
```

#### PyCharm

- You can run individual tests from PyCharm by simply right-clicking a test file, and choosing "Run 'pytest in ...''".
- A test may not work yet on the first try, because the Working directory needs to be adjusted. Go to `Run > Edit Configurations...`. Now select the corresponding run configuration, and set the `Working directory` field to the root directory of the python-mongodb-object-document-mapper project. 


### Docker

It is possible to run application using Docker:

Build Docker image:
```bash
$> docker build -t mongo_odm -f docker/Dockerfile .
```

\[Optional\] Build MongoDB:
```bash
$> docker run --name mongo_db -p 27017:27017 -d mongo
```

Run Docker container, and specify MongoDB and PostgreSQL credentials:
```bash
$> docker run --rm -t \
        -e MONGO_HOST=${MONGO_HOST} \
        -e MONGO_PORT=${MONGO_PORT} \
        mongo_odm -m pytest /tests
```

#### Docker helper script

It is possible to run all the above with helper script:

```bash
$> chmod +x scripts/run_docker.sh
$> scripts/run_docker.sh -m pytest /tests
```

### Docker Compose

It is possible to run application using Docker Compose which includes both **python-mongodb-object-document-mapper** and **mongo**:

Build Docker Compose images:
```bash
$> docker-compose -f docker/docker-compose.yml build
```

Run Docker Compose containers:
```bash
$> docker-compose -f docker/docker-compose.yml run --rm \
       --name ${CONTAINER_NAME} \
       ${CONTAINER_NAME} -m pytest /tests
```

#### Docker Compose helper script

It is possible to run all the above with helper script:

```bash
$> chmod +x scripts/run_docker.sh
$> scripts/run_tests_using_docker_compose.sh
```
