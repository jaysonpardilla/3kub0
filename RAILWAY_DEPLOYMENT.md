# Railway Deployment Guide

This project is configured for production deployment on Railway with WebSocket support via Redis.

## Prerequisites

- Railway account (https://railway.app)
- Railway CLI installed
- Git repository initialized

## Deployment Steps

### 1. Create Railway Project
```bash
railway init
```

### 2. Add Services on Railway Dashboard

#### Add MySQL Database
1. Go to your Railway project
2. Click "Add Service" → "Database" → "MySQL"
3. Set the following environment variables from the created MySQL service:
   - `MYSQL_DATABASE`
   - `MYSQL_HOST`
   - `MYSQL_PORT`
   - `MYSQL_USER`
   - `MYSQL_PASSWORD`

#### Add Redis Service
1. Click "Add Service" → "Database" → "Redis"
2. Copy the `REDIS_URL` from the Redis service

### 3. Configure Environment Variables in Railway

Set the following environment variables in your Railway project settings:

```
DEBUG=False
SECRET_KEY=<generate-a-secure-key>
ALLOWED_HOSTS=your-app-name.railway.app

# MySQL (from Railway MySQL service)
MYSQL_DATABASE=railway
MYSQL_HOST=mysql.railway.internal
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=<from-service>

# Redis (from Railway Redis service)
REDIS_URL=<from-redis-service>

# Cloudinary
CLOUDINARY_URL=cloudinary://786333672776349:KyDW-AJ0wTkcVkcWPrqd_LLRlPg@deyrmzn1x

# Email
EMAIL_HOST_USER=jaysonpardilla278@gmail.com
EMAIL_HOST_PASSWORD=aagx obby uzrp tuhs
DEFAULT_FROM_EMAIL=pardillajayson004@gmail.com

# CORS
CORS_ALLOWED_ORIGINS=https://your-app-name.railway.app
```

### 4. Generate Secure Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Deploy

```bash
git push
```

Railway will automatically detect the Dockerfile and deploy your application.

### 6. Run Initial Migrations

After first deployment, run:

```bash
railway run python manage.py migrate
```

### 7. Create Superuser (Optional)

```bash
railway run python manage.py createsuperuser
```

## Services Architecture

- **Web Service**: Daphne ASGI server for Django + WebSocket support
- **MySQL**: Database service
- **Redis**: Cache and WebSocket message broker for Channels
- **Cloudinary**: Image storage service

## WebSocket Configuration

The project uses:
- **channels**: WebSocket framework
- **channels_redis**: Redis backend for multi-instance WebSocket support
- **daphne**: ASGI server

All WebSocket connections automatically use Redis for message passing, allowing horizontal scaling.

## Important Notes

1. **Redis is Required**: The WebSocket feature requires Redis. Without it, real-time chat won't work.
2. **Migrations**: Ensure migrations run before the app starts
3. **Static Files**: Handled by WhiteNoise middleware
4. **Media Files**: Stored on Cloudinary (not locally)
5. **HTTPS**: Enforced in production (DEBUG=False)

## Troubleshooting

### Check Logs
```bash
railway logs
```

### Connect to Database
```bash
railway connect mysql
```

### Check Redis Connection
```bash
railway run python -c "import redis; r = redis.from_url(os.getenv('REDIS_URL')); print(r.ping())"
```

### Run Django Management Commands
```bash
railway run python manage.py <command>
```

## Local Development

To test locally with production settings:

```bash
DEBUG=False python manage.py runserver
```

Make sure you have Redis running locally:
```bash
redis-cli
```
