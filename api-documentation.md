# API Documentation - Image Processing Service

This document provides information about the available API endpoints, their parameters, and expected responses.

## Base URL

All endpoints are relative to the base URL of the service (e.g., `http://localhost:8000`).

## Authentication

Currently, the API does not implement authentication. This should be added in a production environment.

## Endpoints

### Upload CSV File

Upload a CSV file containing product and image data for processing.

**URL**: `/api/upload`

**Method**: `POST`

**Content-Type**: `multipart/form-data`

**Request Parameters**:
- `file`: CSV file (required)

**CSV Format**:
The CSV file must contain the following columns:
- `S. No.`: Serial number (numeric)
- `Product Name`: Name of the product
- `Input Image Urls`: Comma-separated list of image URLs

**Example CSV**:
```
S. No.,Product Name,Input Image Urls
1,SKU1,https://www.public-image-url1.jpg,https://www.public-image-url2.jpg
2,SKU2,https://www.public-image-url3.jpg,https://www.public-image-url4.jpg
```

**Response**:
```json
{
  "request_id": "64a1b2c3d4e5f6a7b8c9d0e1",
  "message": "CSV file accepted for processing"
}
```

**Status Codes**:
- `200 OK`: CSV file accepted for processing
- `400 Bad Request`: Invalid CSV format or missing required columns
- `500 Internal Server Error`: Server error

### Check Processing Status

Check the status of a processing request.

**URL**: `/api/status/{request_id}`

**Method**: `GET`

**URL Parameters**:
- `request_id`: ID of the processing request (required)

**Query Parameters**:
- `include_products`: Include product details in the response (optional, default: false)

**Response (without products)**:
```json
{
  "request_id": "64a1b2c3d4e5f6a7b8c9d0e1",
  "status": "in_progress",
  "completion_percentage": 45.5,
  "error_message": null
}
```

**Response (with products)**:
```json
{
  "request_id": "64a1b2c3d4e5f6a7b8c9d0e1",
  "status": "completed",
  "completion_percentage": 100.0,
  "error_message": null,
  "products": [
    {
      "serial_number": 1,
      "product_name": "SKU1",
      "input_image_urls": [
        "https://www.public-image-url1.jpg",
        "https://www.public-image-url2.jpg"
      ],
      "output_image_urls": [
        "https://www.public-image-output-url1.jpg",
        "https://www.public-image-output-url2.jpg"
      ]
    }
  ]
}
```

**Status Codes**:
- `200 OK`: Request found
- `400 Bad Request`: Invalid request ID format
- `404 Not Found`: Request not found
- `500 Internal Server Error`: Server error

### Download Results

Get download information for the processed results.

**URL**: `/api/download/{request_id}`

**Method**: `GET`

**URL Parameters**:
- `request_id`: ID of the processing request (required)

**Response**:
```json
{
  "request_id": "64a1b2c3d4e5f6a7b8c9d0e1",
  "status": "completed",
  "message": "Processing completed successfully",
  "download_url": "/api/download/64a1b2c3d4e5f6a7b8c9d0e1/file"
}
```

**Status Codes**:
- `200 OK`: Results available for download
- `400 Bad Request`: Invalid request ID format or processing not completed
- `404 Not Found`: Request not found
- `500 Internal Server Error`: Server error

### Download Results File

Download the actual CSV file with the processing results.

**URL**: `/api/download/{request_id}/file`

**Method**: `GET`

**URL Parameters**:
- `request_id`: ID of the processing request (required)

**Response**:
CSV file with the following format:
```
S. No.,Product Name,Input Image Urls,Output Image Urls
1,SKU1,"https://www.public-image-url1.jpg,https://www.public-image-url2.jpg","https://www.public-image-output-url1.jpg,https://www.public-image-output-url2.jpg"
```

**Status Codes**:
- `200 OK`: File downloaded successfully
- `400 Bad Request`: Invalid request ID format or processing not completed
- `404 Not Found`: Request not found
- `500 Internal Server Error`: Server error

### Health Check

Check if the service is running.

**URL**: `/health`

**Method**: `GET`

**Response**:
```json
{
  "status": "healthy"
}
```

**Status Codes**:
- `200 OK`: Service is running

## Response Codes and Error Handling

### Success Codes
- `200 OK`: Request was successful

### Error Codes
- `400 Bad Request`: Invalid input or request
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Response Format
```json
{
  "detail": "Error message describing the issue"
}
```

## Webhook Integration

If webhook integration is enabled, the system will send a POST request to the configured webhook URL when processing is completed.

**Webhook Payload**:
```json
{
  "request_id": "64a1b2c3d4e5f6a7b8c9d0e1",
  "status": "completed",
  "products": [
    {
      "serial_number": 1,
      "product_name": "SKU1",
      "input_image_urls": ["https://www.public-image-url1.jpg"],
      "output_image_urls": ["https://www.public-image-output-url1.jpg"]
    }
  ],
  "timestamp": "2023-09-25T15:30:45.123Z"
}
```
