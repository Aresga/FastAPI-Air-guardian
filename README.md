# Air Guardian - Backend Service

This project is simple backend service for AirGuardian application, a drone surveillance system designed to detect and log unauthorized drone activity within a protected airspace.

---

## What the Project Does

The AirGuardian backend continuously monitors drone position data from an external API. Its primary function is to detect when a drone enters a designated No-Fly Zone (NFZ), which is defined as a 1000 unit radius circle.

When a violation is detected, the system:
- Fetches the drone owner's personal information from a separate API endpoint.
- Stores the complete violation record, including the drone's position and owner details in a PostgreSQL database.
- Exposes API endpoints to view live drone data and a list of all violations that have occurred within the last 24 hours.

---

## How to Install Dependencies and set up environment variables

All dependencies and environment setup can be handled by the provided Makefile.

1. **Clone the repository.**

	```sh
	git clone git@github.com:Aresga/FastAPI-Air-guardian.git && cd FastAPI-Air-guardian
	```

2. **Install dependencies:**  
   This command uses [Poetry ](#-install-Poetry) to create a virtual environment and install all necessary Python packages.
   ```sh
   make install
   ```
3. **Copy the example.env and populate the variables:**
	```sh
	cp example.env .env
	```
	Open the new ```.env```file and fill in the required values for each variable:
	* ```NFZ_SECRET_KEY```: Secret key for accessing protected endpoints.
	* ```DATABASE_URL```: Connection string for your PostgreSQL database.
	* ```CELERY_BROKER_URL```: Redis URL for Celery message broker.
	* ```BASE_URL```: Base URL for the external drone data API.
	

---

## How to Run the Application Locally

The Makefile provides the easiest way to get started testing.

### Setup the Environment

This command will start the PostgreSQL and Redis containers in Docker and create the necessary database tables.
```sh
make setup
```

### Start All Services

This command launches all three core components of the application in the background:
- **FastAPI Server:** Handles incoming API requests.
- **Celery Worker:** Listens for and executes background jobs (checking for violations).
- **Celery Beat:** The scheduler that triggers the background jobs at a set interval.

```sh
make start
```

Once started, the application will be available at:
- **API Base URL:** http://localhost:8000


### API Endpoints

The AirGuardian backend will exposes the following API endpoints:

- **GET /health**  
	Health check endpoint. Returns a simple status message to confirm the API is running.

- **GET /drones**  
	Returns live data for all drones currently being monitored, including their positions and status.

- **GET /nfz**  
	Returns a list of all drone violation records detected within the last 24 hours.  
	_Requires a valid `X-Secret` header for authentication._


#### Other Useful Commands

- **View Live Logs:**  
  ```sh
  make logs
  ```
- **Stop All Services:**  
  ```sh
  make stop
  ```
- **Restart All Services:**  
  ```sh
  make restart
  ```
- **Clean Up Environment (stops and removes containers and junk files/folders):**  
  ```sh
  make clean
  ```

---

## Manual Local Setup

If you prefer to run the services manually without using make, follow these steps.


### install Poetry

Before running the application, make sure you have poetry installed:

```sh
curl -sSL https://install.python-poetry.org | python3 -
```

```sh
poetry --version
```


### create a virtual environment


```sh
poetry env use python3
```

### Install dependecies


This command will set up a new virtual environment (if one does not already exist) and install all required Python packages as specified in `pyproject.toml`.

```sh
poetry install
```

### Start Services

Ensure Docker is running, then start the required database and message broker containers.

```sh
# Start Redis
docker run -d --name air-guardian-redis -p 6379:6379 redis:7-alpine

# Start PostgreSQL (replace with your credentials)
docker run -d --name air-guardian-postgres \
    -e POSTGRES_USER=user \
    -e POSTGRES_PASSWORD='mypassword' \
    -e POSTGRES_DB=user_db \
    -p 5432:5432 \
    postgres:15
```

### Create Database Tables

After waiting a few moments for the database to initialize, run the table creation script:
```sh
poetry run python create_tables.py
```

### Run the Application

Run the following commands in three separate terminal windows (one command per terminal). Alternatively, you can run them all in a single terminal by appending ```&``` to each command to run it as a background process. (keep track of you pids)

- **Terminal 1: FastAPI Server**
  ```sh
  poetry run uvicorn src.main:app --reload
  ```
- **Terminal 2: Celery Worker**
  ```sh
  poetry run celery -A src.celery_app worker --loglevel=info
  ```
- **Terminal 3: Celery Beat Scheduler**
  ```sh
  poetry run celery -A src.celery_app beat --loglevel=info
  ```

---

## Architectural & Usage Notes

- **Configuration:**  
  The application is configured using environment variables defined in a `.env` file. An `.env.example` file is provided in the repository to show the required variables.

- **Architecture:**
  - **FastAPI:** Serves the public API endpoints.
  - **Celery:** Used for running the periodic background task that fetches drone data every 10 seconds.
  - **PostgreSQL:** The persistent database for storing violation records.
  - **Redis:** Acts as the message broker between the web server and the Celery workers.
  - **/nfz Endpoint:** This endpoint is protected and requires a valid `X-Secret` header to be included in the request to retrieve violation data. If the header is missing or incorrect, the API will return a 401 Unauthorized error.

--- 

