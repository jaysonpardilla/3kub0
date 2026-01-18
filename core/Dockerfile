FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    mysql-client \
    build-essential \
    libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files (including static files)
COPY . .

# Ensure required directories exist
RUN mkdir -p /app/staticfiles /app/core

# Collect static files during build - CRITICAL for production
RUN python manage.py collectstatic --noinput --clear --verbosity 3 || exit 1

# Verify staticfiles were created
RUN ls -la /app/staticfiles/ && echo "Static files collected successfully"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/').read()" || exit 1

# Start server with migrations and ensure static files are collected
CMD sh -c 'python manage.py migrate --noinput && python manage.py collectstatic --noinput && exec daphne -b 0.0.0.0 -p 8000 core.asgi:application'




