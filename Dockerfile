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

# Copy production requirements only
COPY core/requirements-prod.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Copy and make startup script executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Create necessary directories
RUN mkdir -p staticfiles

# Keep working directory at /app
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Use the startup script
CMD ["/app/entrypoint.sh"]
