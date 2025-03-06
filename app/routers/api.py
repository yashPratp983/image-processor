from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse, FileResponse
import logging
from bson import ObjectId
import io

from app.models.models import RequestResponse, StatusResponse, ProcessingStatus
from app.services.csv_service import CSVService
from app.services.db_service import db_service
from app.tasks.worker import process_images

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/api/upload", response_model=RequestResponse)
async def upload_csv(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Upload a CSV file for processing.
    Returns a unique request ID immediately.
    """
    try:
        # Check file extension
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        # Read file content
        contents = await file.read()
        
        # Validate CSV format
        is_valid, error_message, parsed_data = CSVService.validate_csv_format(contents)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Create a new processing request
        request_data = {
            "status": ProcessingStatus.PENDING,
            "products": parsed_data,
            "completion_percentage": 0.0
        }
        
        # Save to database
        request_id = db_service.create_request(request_data)
        
        # Start processing in background
        background_tasks.add_task(process_images.delay, request_id)
        
        return RequestResponse(
            request_id=request_id,
            message="CSV file accepted for processing"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/api/status/{request_id}", response_model=StatusResponse)
async def check_status(request_id: str, include_products: bool = Query(False)):
    """
    Check the status of a processing request.
    Optionally include complete product data.
    """
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(request_id):
            raise HTTPException(status_code=400, detail="Invalid request ID format")
        
        # Get request from database
        request_data = db_service.get_request(request_id)
        
        if not request_data:
            raise HTTPException(status_code=404, detail="Request not found")
        
        # Create response
        response = StatusResponse(
            request_id=request_id,
            status=request_data["status"],
            completion_percentage=request_data.get("completion_percentage", 0.0),
            error_message=request_data.get("error_message")
        )
        
        # Include products if requested
        if include_products:
            response.products = request_data.get("products", [])
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/api/download/{request_id}")
async def download_results(request_id: str):
    """
    Download the processed results as a CSV file.
    Only available for completed requests.
    """
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(request_id):
            raise HTTPException(status_code=400, detail="Invalid request ID format")
        
        # Get request from database
        request_data = db_service.get_request(request_id)
        
        if not request_data:
            raise HTTPException(status_code=404, detail="Request not found")
        
        # Check if processing is complete
        if request_data["status"] != ProcessingStatus.COMPLETED:
            raise HTTPException(
                status_code=400, 
                detail=f"Processing not completed. Current status: {request_data['status']}"
            )
        
        # Generate CSV file
        products = request_data.get("products", [])
        csv_data = CSVService.generate_output_csv(products)
        
        # Create response with CSV file
        return JSONResponse(
            content={
                "request_id": request_id,
                "status": "completed",
                "message": "Processing completed successfully",
                "download_url": f"/api/download/{request_id}/file"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error preparing download: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/api/download/{request_id}/file")
async def download_results_file(request_id: str):
    """
    Download the actual CSV file with processing results.
    """
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(request_id):
            raise HTTPException(status_code=400, detail="Invalid request ID format")
        
        # Get request from database
        request_data = db_service.get_request(request_id)
        
        if not request_data:
            raise HTTPException(status_code=404, detail="Request not found")
        
        # Check if processing is complete
        if request_data["status"] != ProcessingStatus.COMPLETED:
            raise HTTPException(
                status_code=400, 
                detail=f"Processing not completed. Current status: {request_data['status']}"
            )
        
        # Generate CSV file
        products = request_data.get("products", [])
        csv_data = CSVService.generate_output_csv(products)
        
        # Create a temporary file to serve
        filename = f"processed_results_{request_id}.csv"
        
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating download file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")