import logging
import requests
from typing import List, Dict, Any
from celery import shared_task

from app.services.image_service import image_service
from app.services.db_service import db_service
from app.models.models import ProcessingStatus, WebhookPayload
from app.config import WEBHOOK_ENABLED, WEBHOOK_URL

logger = logging.getLogger(__name__)

@shared_task
def process_images(request_id: str):
    """
    Process all images for a request.
    This task coordinates the overall processing and updates status.
    """
    try:
        # Retrieve the request from the database
        request_data = db_service.get_request(request_id)
        if not request_data:
            logger.error(f"Request {request_id} not found")
            return
        
        # Update status to in progress
        db_service.update_request_status(
            request_id, 
            ProcessingStatus.IN_PROGRESS,
            completion_percentage=0
        )
        
        products = request_data.get("products", [])
        total_products = len(products)
        
        # Process each product
        for i, product in enumerate(products):
            # Spawn a task for each product
            process_product_images.delay(
                request_id,
                product["serial_number"],
                product["product_name"],
                product["input_image_urls"]
            )
            
            # Update completion percentage
            completion_percentage = ((i + 1) / total_products) * 100
            db_service.update_request_status(
                request_id,
                ProcessingStatus.IN_PROGRESS,
                completion_percentage=completion_percentage
            )
        
        return f"Processing started for request {request_id} with {total_products} products"
    except Exception as e:
        error_msg = f"Error starting processing for request {request_id}: {str(e)}"
        logger.error(error_msg)
        db_service.update_request_status(
            request_id,
            ProcessingStatus.FAILED,
            error_message=error_msg
        )
        return error_msg

@shared_task
def process_product_images(request_id: str, serial_number: int, 
                          product_name: str, input_image_urls: List[str]):
    """Process all images for a single product"""
    try:
        output_image_urls = []
        
        for image_url in input_image_urls:
            success, output_url, error = image_service.process_image(image_url, product_name)
            if success:
                output_image_urls.append(output_url)
            else:
                logger.error(f"Error processing image {image_url}: {error}")
        
        # Update the product with processed image URLs
        if output_image_urls:
            db_service.update_product_images(request_id, serial_number, output_image_urls)
            
        # Check if all products are processed
        check_request_completion.delay(request_id)
        
        return f"Processed {len(output_image_urls)} images for product {product_name}"
    except Exception as e:
        error_msg = f"Error processing images for product {product_name}: {str(e)}"
        logger.error(error_msg)
        return error_msg

@shared_task
def check_request_completion(request_id: str):
    """Check if all products in a request have been processed"""
    try:
        request_data = db_service.get_request(request_id)
        if not request_data or request_data.get("status") == ProcessingStatus.COMPLETED:
            return
        
        # Check if all products have output image URLs
        products = request_data.get("products", [])
        total_products = len(products)
        processed_products = 0
        
        for product in products:
            if product.get("output_image_urls") and len(product.get("output_image_urls")) > 0:
                processed_products += 1
        
        # Calculate completion percentage
        completion_percentage = (processed_products / total_products) * 100 if total_products > 0 else 0
        
        # Update request status
        if processed_products == total_products:
            db_service.update_request_status(
                request_id,
                ProcessingStatus.COMPLETED,
                completion_percentage=100
            )
            
            # Trigger webhook if enabled
            if WEBHOOK_ENABLED and WEBHOOK_URL:
                trigger_webhook.delay(request_id)
        else:
            db_service.update_request_status(
                request_id,
                ProcessingStatus.IN_PROGRESS,
                completion_percentage=completion_percentage
            )
        
        return f"Request {request_id} completion: {completion_percentage:.2f}%"
    except Exception as e:
        error_msg = f"Error checking completion for request {request_id}: {str(e)}"
        logger.error(error_msg)
        return error_msg

@shared_task
def trigger_webhook(request_id: str):
    """Trigger a webhook to notify about completed processing"""
    if not WEBHOOK_ENABLED or not WEBHOOK_URL:
        return "Webhook not enabled"
    
    try:
        # Get the request data
        request_data = db_service.get_request(request_id)
        if not request_data:
            return f"Request {request_id} not found"
        
        # Prepare webhook payload
        payload = WebhookPayload(
            request_id=request_id,
            status=request_data["status"],
            products=request_data["products"]
        ).dict()
        
        # Send webhook request
        response = requests.post(WEBHOOK_URL, json=payload)
        
        if response.status_code >= 200 and response.status_code < 300:
            logger.info(f"Webhook triggered successfully for request {request_id}")
            return f"Webhook triggered successfully for request {request_id}"
        else:
            error_msg = f"Failed to trigger webhook for request {request_id}. Status: {response.status_code}"
            logger.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"Error triggering webhook for request {request_id}: {str(e)}"
        logger.error(error_msg)
        return error_msg