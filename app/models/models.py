from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ProductImage(BaseModel):
    serial_number: int
    product_name: str
    input_image_urls: List[str]
    output_image_urls: Optional[List[str]] = None


class ProcessingRequest(BaseModel):
    request_id: str
    status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    products: List[ProductImage] = []
    error_message: Optional[str] = None
    completion_percentage: float = 0.0


class RequestResponse(BaseModel):
    request_id: str
    message: str


class StatusResponse(BaseModel):
    request_id: str
    status: ProcessingStatus
    completion_percentage: float
    products: Optional[List[ProductImage]] = None
    error_message: Optional[str] = None


class WebhookPayload(BaseModel):
    request_id: str
    status: ProcessingStatus
    products: List[ProductImage]
    timestamp: datetime = Field(default_factory=datetime.utcnow)