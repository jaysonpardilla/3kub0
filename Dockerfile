FROM python:3.11-slim

# Build cache invalidation - forces rebuild
ARG BUILD_DATE=2026-01-18-twisted-iocpsupport-removed-v2

# Simplified build - using Python packages for database connectivity
WORKDIR /app

# Install build dependencies AND OpenCV runtime libraries
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    pkg-config \
    libmariadb-dev \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy production requirements only
COPY core/requirements-prod.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Copy Python startup script
COPY startup.py /app/startup.py

# Create necessary directories
RUN mkdir -p staticfiles

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Use exec form with Python - no shell needed
CMD ["python", "/app/startup.py"]
