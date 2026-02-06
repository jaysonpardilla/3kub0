from PIL import Image
import io
from django.core.files.base import ContentFile
import numpy as np


def remove_background_from_uploaded_file(uploaded_file, output_format='PNG'):
    """Attempt to remove background using rembg. If rembg or its native deps
    aren't available, return the original image bytes as a ContentFile.

    This function performs a lazy import of rembg to avoid importing heavy
    native libraries (onnxruntime) at Django startup.
    """
    import cv2
    
    # Attempt rembg first (lazy import)
    try:
        from rembg import remove
        try:
            uploaded_file.seek(0)
            input_image = Image.open(uploaded_file).convert("RGBA")
            result = remove(input_image)
            buffer = io.BytesIO()
            result.save(buffer, format=output_format)
            buffer.seek(0)
            return ContentFile(buffer.getvalue())
        except Exception:
            # fall through to OpenCV fallback
            pass
    except Exception:
        # rembg not available or failed to import — proceed to OpenCV fallback
        pass

    # OpenCV GrabCut fallback (works without onnxruntime)
    try:
        uploaded_file.seek(0)
        with Image.open(uploaded_file) as pil_img:
            pil_img = pil_img.convert("RGBA")
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGBA2BGR)

        # Prepare mask and models
        mask = np.zeros(img.shape[:2], np.uint8)
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)

        h, w = img.shape[:2]
        # use a rect slightly inside the image to assume foreground center
        rect = (int(w * 0.05), int(h * 0.05), int(w * 0.9), int(h * 0.9))

        cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
        # mask==2 or mask==0 are background; 1 or 3 are foreground
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        img_rgb[:, :, 3] = mask2 * 255

        result_pil = Image.fromarray(img_rgb)
        buffer = io.BytesIO()
        result_pil.save(buffer, format=output_format)
        buffer.seek(0)
        return ContentFile(buffer.getvalue())
    except Exception:
        # final fallback: return original bytes
        try:
            uploaded_file.seek(0)
            return ContentFile(uploaded_file.read())
        except Exception:
            return None


def build_cloudinary_url(public_id_or_url, cloud_name=None):
    """
    Construct a proper Cloudinary URL from a public_id or URL.
    
    IMPORTANT: This function is for DISPLAY only. Never store full URLs in the database.
    Store only the public_id (relative path like 'product_images/bg_x.png').
    """
    import re
    
    try:
        if not public_id_or_url:
            return ''

        s = str(public_id_or_url).strip()
        
        # Determine cloud name
        if not cloud_name:
            from django.conf import settings
            cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'deyrmzn1x')

        # Case 1: Already a clean full URL (starts with https://res.cloudinary.com/)
        # Return as-is, but normalize any missing slashes
        if s.startswith('https://res.cloudinary.com/'):
            # Fix missing slash in https:/ -> https://
            s = re.sub(r'https:/res\.cloudinary\.com', 'https://res.cloudinary.com', s)
            return s
        
        # Case 2: Contains res.cloudinary.com but is malformed (possibly corrupted)
        # Example: https:/res.cloudinary.com/... or has version numbers embedded
        if 'res.cloudinary.com' in s:
            # Try to extract the public_id from anywhere in the string
            # Look for patterns like 'product_images/file.png' or similar
            
            # Find the last segment that looks like a file path (contains / and has extension)
            parts = s.split('/')
            public_part = None
            for i in range(len(parts) - 1, -1, -1):
                part = parts[i]
                # Check if this part looks like a public_id (has extension and doesn't start with http)
                if '.' in part and not part.startswith('http'):
                    # This might be the public_id, but we need to check previous parts too
                    # Construct the full path from this part onwards
                    candidate = '/'.join(parts[i:])
                    # Clean up any version numbers
                    candidate = re.sub(r'^v\d+/', '', candidate)
                    # Clean up any http fragments
                    candidate = re.sub(r'https:?/?/?res\.cloudinary\.com/?', '', candidate)
                    candidate = re.sub(r'^/?/?', '', candidate)
                    if candidate and not candidate.startswith('http'):
                        public_part = candidate
                        break
            
            if public_part:
                # Extract filename and extension
                if '.' in public_part:
                    base, ext = public_part.rsplit('.', 1)
                    if len(ext) <= 4:  # Valid extension
                        return f"https://res.cloudinary.com/{cloud_name}/image/upload/{base}.{ext}"
                return f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_part}.png"
            
            # Last resort: return empty to trigger fallback
            return ''
        
        # Case 3: Normal relative path (what we should be storing in DB)
        # Just construct the full URL
        # Normalize: drop leading slashes
        s = s.lstrip('/')
        
        # If it already contains upload path, take the part after it
        if '/image/upload/' in s:
            s = s.split('/image/upload/')[-1]
        
        # Clean up any version numbers at the start
        s = re.sub(r'^v\d+/', '', s)
        
        # If s has an extension, use it
        if '.' in s:
            base, ext = s.rsplit('.', 1)
            if len(ext) <= 4:
                return f"https://res.cloudinary.com/{cloud_name}/image/upload/{base}.{ext}"
        
        # Fallback: assume png
        return f"https://res.cloudinary.com/{cloud_name}/image/upload/{s}.png"
        
    except Exception:
        return ''
