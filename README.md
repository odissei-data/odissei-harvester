Absolutely, I've integrated the expected input and output for the different endpoints using the provided schemas and models. Here's the updated README with the additional information:

---

# FastAPI Harvester

A FastAPI application for harvesting metadata from external sources and storing it in an AWS S3 bucket.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Endpoints](#endpoints)
- [Background Tasks](#background-tasks)
- [Dockerization](#dockerization)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your_username/fastapi-harvester.git
   ```

## Usage

This FastAPI application allows you to initiate harvesting processes for metadata from external sources and store it in an AWS S3 bucket. It provides various API endpoints to start and monitor the harvesting processes.

## Configuration

The following environment variables need to be set for proper functioning:

- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key.
- `AWS_ACCESS_KEY_ID`: Your AWS access key ID.
- `S3_STORAGE_ENDPOINT`: The endpoint URL for your S3 storage.
- `LISS_ENDPOINT_URL`: The URL of the LISS API for metadata harvesting.
- `LISS_ENDPOINT_USERNAME`: Your LISS API username.
- `LISS_ENDPOINT_KEY`: Your LISS API key.

## Endpoints

### `/version`

**Method:** GET

**Description:** Get the version of the FastAPI Harvester.

**Input:** None

**Output:** JSON containing the version of the FastAPI Harvester.

### `/harvest_status/{harvest_id}`

**Method:** GET

**Description:** Get the status of a specific harvesting process.

**Input:** `harvest_id` - The unique ID of the harvesting process.

**Output:** JSON containing the details of the new harvesting process, including its ID, status, start time, end time, and failed files.

### `/start_liss_harvest_background`

**Method:** POST

**Description:** Initiate a background LISS metadata harvesting process.

**Input:** JSON body containing `LISSRequest` data, specifying the bucket name for storage.

**Output:** JSON containing the details of the new harvesting process, including its ID, status, start time, end time, and failed files.

### `/start_liss_harvest`

**Method:** POST

**Description:** Initiate a LISS metadata harvesting process.

**Input:** JSON body containing `LISSRequest` data, specifying the bucket name for storage.

**Output:** JSON containing the details of the new harvesting process, including its ID, status, start time, and more.

### `/start_harvest_background`

**Method:** POST

**Description:** Initiate a background metadata harvesting process.

**Input:** JSON body containing `HarvestRequest` data, specifying metadata prefix, OAI endpoint, bucket name, and more.

**Output:** JSON containing the details of the new harvesting process, including its ID, status, start time, and more.

### `/start_harvest`

**Method:** POST

**Description:** Initiate a metadata harvesting process.

**Input:** JSON body containing `HarvestRequest` data, specifying metadata prefix, OAI endpoint, bucket name, and more.

**Output:** JSON containing the details of the new harvesting process, including its ID, status, start time, and more.

## Background Tasks

Background tasks are used to perform metadata harvesting asynchronously. They are employed to ensure efficient processing and handling of large amounts of data.

## Dockerization

To run the FastAPI Harvester using Docker, follow these steps:

1. Make sure you have Docker installed on your system.

2. Create a `.env` file in the root directory of the project with the environment variables mentioned above.

3. Build and start the containers using Docker Compose:

   ```bash
   docker-compose up --build
   ```

   This will build the Docker image and start the FastAPI application along with a PostgreSQL database container.

4. Access the FastAPI application at `http://localhost:7890`.


## License

This project is licensed under the [Apache license](LICENSE).
