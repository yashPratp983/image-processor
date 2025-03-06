# Image Processing Service

## Running Instructions

Follow these steps to set up and run the Image Processing Service.

### Prerequisites

- Docker and Docker Compose installed
- Git (optional, for cloning the repository)

## Setup

### Clone the repository (or download the source code)

```bash
git clone https://github.com/yourusername/image-processor.git
cd image-processor
```

### Create a `.env` file in the project root (optional, defaults are provided in code)

```
MONGODB_URL=mongodb://mongo:27017
MONGODB_DB_NAME=image_processor_db
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
OUTPUT_IMAGE_DIR=/app/processed_images
OUTPUT_IMAGE_BASE_URL=http://localhost:8000/images/
WEBHOOK_ENABLED=false
WEBHOOK_URL=
```

## Starting the Services

### Build and start the services using Docker Compose

```bash
docker-compose up -d
```

### Check if all services are running

```bash
docker-compose ps
```

You should see the following services running:

- `image_processor_api`
- `image_processor_worker`
- `image_processor_mongo`
- `image_processor_redis`

### Check the logs for any errors

```bash
docker-compose logs
```

## Running Without Docker (Alternative)

If you prefer to run the services without Docker:

### Install the required dependencies

```bash
pip install -r requirements.txt
```

### Start MongoDB and Redis (you need to have them installed)

### Start the FastAPI server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Start the Celery worker in a separate terminal

```bash
celery -A celery_app worker --loglevel=info
```

## Testing the Service

### Access the API documentation

[Swagger UI](http://localhost:8000/docs)

### API Endpoints

- **Upload a CSV file**: `POST /api/upload`
- **Check processing status**: `GET /api/status/{request_id}`
- **Download results**: `GET /api/download/{request_id}`

### Creating a Test CSV File

Use the following format for testing:

```
S. No.,Product Name,Input Image Urls
1,SKU1,https://picsum.photos/200/300,https://picsum.photos/300/400
2,SKU2,https://picsum.photos/400/500,https://picsum.photos/500/600
```

Save this as `test.csv` and upload it using the `/api/upload` endpoint.

## Troubleshooting

### API Service Not Starting

- Check the logs: `docker-compose logs api`
- Ensure MongoDB and Redis are running
- Verify environment variables are set correctly

### Celery Worker Not Processing Tasks

- Check the logs: `docker-compose logs worker`
- Ensure Redis is running and accessible
- Verify Celery worker is connected to the broker

### Images Not Processing

- Check if the URLs in the CSV file are accessible
- Verify the `OUTPUT_IMAGE_DIR` directory exists and is writable
- Check the logs for any errors during image processing

### Database Issues

- Verify MongoDB is running: `docker-compose logs mongo`
- Check database connection string
- Ensure database user has correct permissions

## Shutting Down

To stop all services:

```bash
docker-compose down
```

To stop and remove all data (including volumes):

```bash
docker-compose down -v
```
