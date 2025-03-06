import os
import requests
from PIL import Image
import io
import uuid
import logging
from typing import Tuple, Optional
import time

from app.config import COMPRESSION_QUALITY, OUTPUT_IMAGE_DIR, OUTPUT_IMAGE_BASE_URL

logger = logging.getLogger(__name__)

class ImageService:
    def __init__(self):
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_IMAGE_DIR, exist_ok=True)
    
    def download_image(self, image_url: str) -> Optional[bytes]:
        """Download an image from a URL"""
        try:
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"Failed to download image from {image_url}, status code: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error downloading image from {image_url}: {str(e)}")
            return None
    
    def compress_image(self, image_data: bytes) -> Optional[bytes]:
        """Compress an image to 50% of its original quality"""
        try:
            img = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if it's in another mode that doesn't support JPEG
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=COMPRESSION_QUALITY)
            return output.getvalue()
        except Exception as e:
            logger.error(f"Error compressing image: {str(e)}")
            return None
    
    def save_image(self, image_data: bytes, product_name: str) -> Tuple[bool, str]:
        """Save a compressed image to disk and return its URL"""
        try:
            # Generate a unique filename
            filename = f"{product_name.replace(' ', '_')}_{uuid.uuid4()}.jpg"
            file_path = os.path.join(OUTPUT_IMAGE_DIR, filename)
            
            # Write the image to disk
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            # Return the public URL
            image_url = f"{OUTPUT_IMAGE_BASE_URL.rstrip('/')}/{filename}"
            return True, image_url
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")
            return False, ""
    
    def process_image(self, image_url: str, product_name: str) -> Tuple[bool, str, str]:
        """
        Process an image - download, compress, and save
        Returns: (success, output_url, error_message)
        """
        try:
            # Add a small delay to avoid overwhelming external servers
            time.sleep(0.5)
            
            # Download the image
            image_data = self.download_image(image_url)
            if not image_data:
                return False, "", f"Failed to download image from {image_url}"
            
            # Compress the image
            compressed_data = self.compress_image(image_data)
            if not compressed_data:
                return False, "", f"Failed to compress image from {image_url}"
            
            # Save the compressed image
            success, output_url = self.save_image(compressed_data, product_name)
            if not success:
                return False, "", f"Failed to save processed image from {image_url}"
            
            return True, output_url, ""
        except Exception as e:
            error_msg = f"Error processing image {image_url}: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg

image_service = ImageService()