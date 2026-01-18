# Static Files MIME Type Error - Fix Guide

## Problem Summary
Browser console shows: `Refused to apply style/script because its MIME type ('text/html') is not a supported stylesheet/executable MIME type`

This occurs when static files (CSS, JS) are served with incorrect `text/html` MIME type instead of `text/css` or `application/javascript`.

## Root Causes Fixed

### 1. **Missing WhiteNoise Storage Configuration**
- **Issue**: WhiteNoise middleware was installed but not configured to serve static files properly
- **Fix**: Added `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'` in `settings.py`
- **Why**: This tells Django to use WhiteNoise's optimized static file storage with proper MIME type handling

### 2. **Incorrect Content Security Policy (CSP)**
- **Issue**: CSP header was too permissive (`'default-src': ("'self'", 'https:')`)
- **Fix**: Updated CSP to explicitly allow static files:
  ```python
  SECURE_CONTENT_SECURITY_POLICY = {
      'default-src': ("'self'",),
      'script-src': ("'self'", "'unsafe-inline'"),
      'style-src': ("'self'", "'unsafe-inline'"),
      'font-src': ("'self'",),
      'img-src': ("'self'", 'data:', 'https:'),
      'connect-src': ("'self'",),
  }
  ```
- **Why**: Properly configured CSP allows browsers to load static files from the same origin

### 3. **Docker Build Process**
- **Issue**: `collectstatic` command wasn't being run during build properly
- **Fix**: Improved Dockerfile with:
  - Added error handling (`|| exit 1`)
  - Added verbose logging for debugging
  - Ensured `collectstatic` runs both at build-time and runtime
  - Added `--no-default-ignore` flag to ensure all files are collected
- **Why**: Static files must be collected into the `STATIC_ROOT` directory before serving

### 4. **MIME Type Mapping**
- **Issue**: Python/Django might not recognize custom file MIME types
- **Fix**: Added explicit MIME type mappings:
  ```python
  MIMETYPES = {
      '.css': 'text/css',
      '.js': 'application/javascript',
      '.json': 'application/json',
      '.woff': 'font/woff',
      '.woff2': 'font/woff2',
      '.ttf': 'font/ttf',
      '.eot': 'application/vnd.ms-fontobject',
      '.svg': 'image/svg+xml',
  }
  ```

## Changes Made

### File: `core/settings.py`
- ✅ Added WhiteNoise storage configuration
- ✅ Updated static files settings with proper documentation
- ✅ Fixed CSP security headers for static file serving
- ✅ Added MIME type mappings

### File: `Dockerfile`
- ✅ Improved `collectstatic` command with error checking
- ✅ Added verbose logging for debugging
- ✅ Ensured static files collected at both build and runtime

## How to Deploy

1. **Push changes to your repository**
   ```bash
   git add core/settings.py Dockerfile
   git commit -m "Fix: Static files MIME type issues with WhiteNoise configuration"
   git push origin main
   ```

2. **Redeploy on Railway**
   - Go to Railway dashboard
   - Trigger a new deployment
   - The Docker build will now properly collect static files

3. **Verify Fix**
   - Check Chrome DevTools Console (F12 → Console tab)
   - CSS/JS files should load without MIME type errors
   - Network tab should show CSS/JS with proper MIME types

## Expected Results After Fix

- ✅ Browser console: No MIME type errors
- ✅ CSS styling applies to pages
- ✅ JavaScript functionality works
- ✅ Images and fonts load properly
- ✅ 404 errors for missing resources

## Troubleshooting

If issues persist after deployment:

1. **Clear Browser Cache**
   - Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)

2. **Check Railway Logs**
   - Go to Railway dashboard → Logs
   - Search for "collectstatic" to verify static files were collected

3. **Verify Static Files Folder**
   ```bash
   # In Railway terminal
   ls -la /app/staticfiles/
   ```

4. **Check Django Settings**
   ```bash
   python manage.py findstatic --list
   ```

## Key Configuration Settings

```python
# Static Files Settings
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Middleware (order matters!)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Must be after SecurityMiddleware
    # ... other middleware
]
```

## Additional Notes

- WhiteNoise is production-ready and recommended by Django for serving static files
- The middleware MUST be placed after `SecurityMiddleware` in the MIDDLEWARE list
- `CompressedManifestStaticFilesStorage` automatically compresses CSS/JS and adds cache-busting hashes
- CSP headers are properly configured to allow scripts/styles from same origin only

## References

- [WhiteNoise Documentation](http://whitenoise.evans.io/)
- [Django Static Files Documentation](https://docs.djangoproject.com/en/stable/howto/static-files/)
- [MIME Types Reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types)
