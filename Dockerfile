FROM python:3.10-slim  
WORKDIR /app  

# Install dependencies
COPY requirements.txt .

# First install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Then install Python dependencies with specific instructions for numpy/pandas
RUN pip install --no-cache-dir numpy
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pandas

# Copy application code
COPY . .  

# Create directories
RUN mkdir -p processed_images  

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1  

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]