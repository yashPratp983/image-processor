from pymongo import MongoClient
from bson import ObjectId
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.config import MONGODB_URL, MONGODB_DB_NAME, REQUESTS_COLLECTION, PRODUCTS_COLLECTION
from app.models.models import ProcessingStatus, ProcessingRequest

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client[MONGODB_DB_NAME]
        self.requests_collection = self.db[REQUESTS_COLLECTION]
        self.products_collection = self.db[PRODUCTS_COLLECTION]
    
    def create_request(self, request_data: Dict[str, Any]) -> str:
        """Create a new processing request in the database"""
        result = self.requests_collection.insert_one(request_data)
        return str(result.inserted_id)
    
    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get a processing request by ID"""
        try:
            request = self.requests_collection.find_one({"_id": ObjectId(request_id)})
            if request:
                request["request_id"] = str(request["_id"])
            return request
        except Exception as e:
            logger.error(f"Error retrieving request {request_id}: {str(e)}")
            return None
    
    def update_request_status(self, request_id: str, status: ProcessingStatus, 
                              completion_percentage: float = None,
                              error_message: str = None) -> bool:
        """Update the status of a processing request"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            if completion_percentage is not None:
                update_data["completion_percentage"] = completion_percentage
                
            if error_message is not None:
                update_data["error_message"] = error_message
                
            result = self.requests_collection.update_one(
                {"_id": ObjectId(request_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating request {request_id}: {str(e)}")
            return False
    
    def update_product_images(self, request_id: str, serial_number: int, 
                              output_image_urls: List[str]) -> bool:
        """Update the output image URLs for a product in a request"""
        try:
            result = self.requests_collection.update_one(
                {
                    "_id": ObjectId(request_id),
                    "products.serial_number": serial_number
                },
                {
                    "$set": {
                        "products.$.output_image_urls": output_image_urls,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating product images for request {request_id}, product {serial_number}: {str(e)}")
            return False
    
    def save_product(self, product_data: Dict[str, Any]) -> str:
        """Save a product to the database"""
        result = self.products_collection.insert_one(product_data)
        return str(result.inserted_id)

db_service = DatabaseService()