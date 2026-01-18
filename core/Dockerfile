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

# Create necessary directories
RUN mkdir -p /app/staticfiles

# Collect static files - Critical for WhiteNoise
RUN echo "Collecting static files..." && \
    python manage.py collectstatic --noinput --clear --verbosity 2 && \
    echo "Static files collection complete" && \
    find /app/staticfiles -type f | head -20

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/').read()" || exit 1

# Run migrations and start Daphne with WhiteNoise
CMD sh -c 'echo "Starting Django app..." && \
    python manage.py migrate --noinput && \
    echo "Collecting static files at startup..." && \
    python manage.py collectstatic --noinput && \
    echo "Starting Daphne server..." && \
    exec daphne -b 0.0.0.0 -p 8000 core.asgi:application'




