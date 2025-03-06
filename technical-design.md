# Image Processing System: Technical Design Document

## 1. System Overview

The Image Processing System is designed to efficiently process image data from CSV files. The system receives CSV files containing product information and image URLs, processes these images by compressing them, and provides APIs to track the status of the processing.

## 2. Architecture

The system is built using the following technologies:
- **FastAPI**: For creating the REST API endpoints
- **Celery**: For asynchronous processing of images
- **MongoDB**: For storing request and product data
- **Redis**: As the message broker for Celery

The architecture follows a microservices approach with the following components:
1. **API Service**: Handles HTTP requests, validates input data, and initiates processing
2. **Worker Service**: Processes images asynchronously
3. **Database Service**: Manages data persistence
4. **Broker Service**: Facilitates communication between components

## 3. Component Details

### 3.1 API Service (FastAPI)

The API Service exposes the following endpoints:
- `/api/upload`: Accepts CSV files, validates them, and initiates processing
- `/api/status/{request_id}`: Checks the status of a processing request
- `/api/download/{request_id}`: Downloads the processed results

The API Service is responsible for:
- Validating the CSV format
- Creating processing requests in the database
- Returning unique request IDs to clients
- Queuing processing tasks in Celery

### 3.2 Worker Service (Celery)

The Worker Service processes images asynchronously. It includes the following tasks:
- `process_images`: Coordinates the overall processing for a request
- `process_product_images`: Processes images for a specific product
- `check_request_completion`: Checks if all processing is complete
- `trigger_webhook`: Notifies external systems upon completion

The Worker Service is responsible for:
- Downloading images from provided URLs
- Compressing images to 50% quality
- Storing processed images
- Updating processing status in the database
- Triggering webhooks when processing is complete

### 3.3 Database Service (MongoDB)

The Database Service stores and manages the following data:
- Processing requests
- Product information
- Image URLs (original and processed)
- Processing status

### 3.4 Broker Service (Redis)

The Broker Service facilitates communication between the API Service and Worker Service. It is responsible for:
- Queuing tasks for processing
- Storing task results
- Managing task status

## 4. Data Flow

1. **CSV Upload**:
   - Client uploads a CSV file via the `/api/upload` endpoint
   - System validates the CSV format
   - System creates a processing request in the database
   - System returns a unique request ID to the client
   - System queues the processing task in Celery

2. **Image Processing**:
   - Celery worker picks up the processing task
   - Worker retrieves the request data from the database
   - Worker updates the request status to "in_progress"
   - Worker processes each product's images:
     - Downloads images from provided URLs
     - Compresses images to 50% quality
     - Saves processed images
     - Updates product data with processed image URLs
   - Worker updates the completion percentage as processing progresses
   - Worker marks the request as "completed" when all processing is done
   - Worker triggers a webhook if configured

3. **Status Check**:
   - Client queries the status of a request via the `/api/status/{request_id}` endpoint
   - System retrieves the request status from the database
   - System returns the status and completion percentage to the client

4. **Result Download**:
   - Client downloads the processed results via the `/api/download/{request_id}` endpoint
   - System generates a CSV file with the processed data
   - System returns the CSV file to the client

## 5. Database Schema

### 5.1 Processing Requests Collection

```
{
    "_id": ObjectId,
    "status": String (enum: "pending", "in_progress", "completed", "failed"),
    "created_at": DateTime,
    "updated_at": DateTime,
    "completion_percentage": Float,
    "error_message": String (optional),
    "products": [
        {
            "serial_number": Integer,
            "product_name": String,
            "input_image_urls": [String],
            "output_image_urls": [String]
        }
    ]
}
```

### 5.2 Products Collection (Optional)

```
{
    "_id": ObjectId,
    "serial_number": Integer,
    "product_name": String,
    "request_id": ObjectId,
    "input_image_urls": [String],
    "output_image_urls": [String],
    "created_at": DateTime,
    "updated_at": DateTime
}
```

## 6. Error Handling

The system implements robust error handling at multiple levels:
- **API Level**: HTTP exceptions with appropriate status codes
- **Task Level**: Error capturing and reporting in Celery tasks
- **Database Level**: Exception handling for database operations
- **Image Processing Level**: Error handling for image download and processing

Errors are logged and, where appropriate, stored in the database for client access.

## 7. Scalability Considerations

The system is designed to be scalable:
- **Horizontal Scaling**: Multiple API and worker instances can be deployed
- **Task Distribution**: Celery distributes tasks across multiple workers
- **Database Scaling**: MongoDB can be scaled through sharding
- **Statelessness**: Components are stateless, allowing for elastic scaling

## 8. Security Considerations

- Input validation to prevent injection attacks
- Rate limiting to prevent abuse
- Authentication (to be implemented as needed)
- CORS protection
- Error handling that doesn't leak sensitive information

## 9. Deployment

The system is containerized using Docker and can be deployed using Docker Compose:
- **API Container**: Runs the FastAPI application
- **Worker Container**: Runs the Celery workers
- **MongoDB Container**: Runs the MongoDB database
- **Redis Container**: Runs the Redis broker

## 10. Monitoring and Logging

- Structured logging at all levels
- Health check endpoints
- Celery task monitoring
- Database query monitoring
