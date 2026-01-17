FROM python:3.12-slim

WORKDIR /app

# Install system dependencies required for MySQL
RUN apt-get update && apt-get install -y \
    gcc \
    mysql-client \
    build-essential \
    libmysqlclient-dev \
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

# Make sure we have permissions
RUN chmod +x /app/start.sh || true

# Expose port
EXPOSE 8000

# Start the application
CMD ["sh", "-c", "python manage.py migrate && daphne -b 0.0.0.0 -p 8000 core.asgi:application"]

