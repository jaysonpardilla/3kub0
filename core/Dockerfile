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

# Pre-create staticfiles directory with proper permissions
RUN mkdir -p /app/staticfiles && chmod 755 /app/staticfiles

# Run migrations first
RUN echo "Running migrations..." && \
    python manage.py migrate --noinput || echo "Warning: Migrations had issues, continuing..."

# Collect static files BEFORE starting server - this is CRITICAL
RUN echo "Collecting static files..." && \
    python manage.py collectstatic --noinput --clear --verbosity 3 && \
    echo "Static file collection complete" && \
    echo "Listing staticfiles directory:" && \
    find /app/staticfiles -type f -name "*.css" -o -name "*.js" | head -20 && \
    echo "Total files in staticfiles:" && \
    find /app/staticfiles -type f | wc -l

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/').read()" || exit 1

# Start Daphne with WhiteNoise serving static files
CMD exec daphne -b 0.0.0.0 -p 8000 core.asgi:application




