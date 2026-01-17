FROM python:3.11-slim

# Build cache invalidation - forces rebuild
ARG BUILD_DATE=2026-01-18-force-refresh

# Simplified build - using Python packages for database connectivity
WORKDIR /app

# Install only essential build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    pkg-config \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from core directory
COPY core/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Create necessary directories
RUN mkdir -p staticfiles

# Set working directory to core
WORKDIR /app/core

# Expose port
EXPOSE 8000

# Start the application
CMD ["sh", "-c", "python manage.py migrate && daphne -b 0.0.0.0 -p 8000 core.asgi:application"]
