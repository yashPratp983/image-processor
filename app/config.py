import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "image_processor_db")
REQUESTS_COLLECTION = "processing_requests"
PRODUCTS_COLLECTION = "products"

# Celery settings
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Image processing settings
COMPRESSION_QUALITY = 50  # 50% of original quality
OUTPUT_IMAGE_DIR = os.getenv("OUTPUT_IMAGE_DIR", "./processed_images")
OUTPUT_IMAGE_BASE_URL = os.getenv("OUTPUT_IMAGE_BASE_URL", "https://example.com/images/")

# Webhook settings
WEBHOOK_ENABLED = os.getenv("WEBHOOK_ENABLED", "false").lower() == "true"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")