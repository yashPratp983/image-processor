import pandas as pd
from typing import List, Dict, Any, Tuple
import logging
import io

from app.models.models import ProductImage, ProcessingStatus

logger = logging.getLogger(__name__)

class CSVService:
    REQUIRED_COLUMNS = ["S. No.", "Product Name", "Input Image Urls"]
    
    @staticmethod
    def validate_csv_format(file_contents: bytes) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Validate the CSV file format and return parsed data if valid
        Returns: (is_valid, error_message, parsed_data)
        """
        try:
            # Read CSV file
            df = pd.read_csv(io.BytesIO(file_contents))
            
            # Check required columns
            for col in CSVService.REQUIRED_COLUMNS:
                if col not in df.columns:
                    return False, f"Missing required column: {col}", []
            
            # Validate data types and non-empty values
            if df.empty:
                return False, "CSV file is empty", []
            
            # Check if S. No. column contains numeric values
            if not pd.to_numeric(df["S. No."], errors='coerce').notnull().all():
                return False, "Serial numbers must be numeric", []
            
            # Check for empty product names
            if df["Product Name"].isnull().any():
                return False, "Product names cannot be empty", []
                
            # Check for empty image URLs
            if df["Input Image Urls"].isnull().any():
                return False, "Input image URLs cannot be empty", []
            
            # Parse the data into the required format
            parsed_data = []
            for _, row in df.iterrows():
                image_urls = [url.strip() for url in row["Input Image Urls"].split(",") if url.strip()]
                if not image_urls:
                    return False, f"No valid image URLs for product: {row['Product Name']}", []
                
                product_data = {
                    "serial_number": int(row["S. No."]),
                    "product_name": row["Product Name"],
                    "input_image_urls": image_urls,
                    "output_image_urls": []
                }
                parsed_data.append(product_data)
            
            return True, "", parsed_data
        except Exception as e:
            logger.error(f"Error validating CSV: {str(e)}")
            return False, f"Error processing CSV file: {str(e)}", []
    
    @staticmethod
    def generate_output_csv(products: List[ProductImage]) -> bytes:
        """Generate an output CSV file with processed image URLs"""
        data = []
        for product in products:
            data.append({
                "S. No.": product.serial_number,
                "Product Name": product.product_name,
                "Input Image Urls": ",".join(product.input_image_urls),
                "Output Image Urls": ",".join(product.output_image_urls or [])
            })
        
        df = pd.DataFrame(data)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        return csv_buffer.getvalue().encode()