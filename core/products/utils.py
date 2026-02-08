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
            return buffer
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
    
    Handles the following cases:
    1. Already a clean full URL (returns as-is)
    2. Duplicated URL pattern: https://res.cloudinary.com/.../https:/res.cloudinary.com/... (extracts public_id)
    3. Malformed URL with res.cloudinary.com (extracts public_id)
    4. Normal relative path (constructs full URL)
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

        # Case 0: Handle duplicated or nested Cloudinary URLs robustly.
        # Sometimes the stored value contains multiple '/image/upload/' segments
        # e.g. '.../image/upload/v123/https:/res.cloudinary.com/.../image/upload/user_profiles/xxx.jpg'
        # Strategy: always take the text after the last '/image/upload/' and treat
        # that as the public_id (remove version prefix if present).
        if 'res.cloudinary.com' in s and '/image/upload/' in s:
            # take the substring after the last /image/upload/
            public_id = s.split('/image/upload/')[-1]
            # If the extracted part still contains another cloudinary URL, keep taking last segment
            while 'res.cloudinary.com' in public_id and '/image/upload/' in public_id:
                public_id = public_id.split('/image/upload/')[-1]

            public_id = public_id.lstrip('/')
            public_id = re.sub(r'^v\d+/', '', public_id)
            # If it's a full URL fragment like 'https:/res.cloudinary.com/...', strip any schema/host
            public_id = re.sub(r'https?:/*res\.cloudinary\.com[^/]*/image/upload/*', '', public_id)
            public_id = public_id.lstrip('/')
            if public_id:
                # If no extension, assume png
                if '.' not in public_id:
                    public_id = f"{public_id}.png"
                return f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"

        # Case 1: Already a clean full URL (starts with https://res.cloudinary.com/)
        # Return as-is, but normalize any missing slashes
        if s.startswith('https://res.cloudinary.com/'):
            # Fix missing slash in https:/ -> https://
            s = re.sub(r'https:/res\.cloudinary\.com', 'https://res.cloudinary.com', s)
            # Also handle case where version number is followed by another URL
            s = re.sub(r'(https://res\.cloudinary\.com/[^/]+/image/upload/)v\d+/https://', r'\1', s)
            return s
        
        # Case 2: Contains res.cloudinary.com but is malformed (possibly corrupted)
        if 'res.cloudinary.com' in s:
            parts = s.split('/')
            public_part = None
            for i in range(len(parts) - 1, -1, -1):
                part = parts[i]
                if '.' in part and not part.startswith('http'):
                    candidate = '/'.join(parts[i:])
                    candidate = re.sub(r'^v\d+/', '', candidate)
                    candidate = re.sub(r'https:?/?/?res\.cloudinary\.com/?', '', candidate)
                    candidate = re.sub(r'^/?/?', '', candidate)
                    if candidate and not candidate.startswith('http'):
                        public_part = candidate
                        break
            
            if public_part:
                # If already has extension, use it
                if '.' in public_part:
                    base, ext = public_part.rsplit('.', 1)
                    if len(ext) <= 4:
                        return f"https://res.cloudinary.com/{cloud_name}/image/upload/{base}.{ext}"
                # Otherwise add png extension
                return f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_part}.png"
            
            return ''
        
        # Case 3: Normal relative path
        s = s.lstrip('/')
        
        if '/image/upload/' in s:
            s = s.split('/image/upload/')[-1]
        
        s = re.sub(r'^v\d+/', '', s)
        
        # If s has an extension, use it
        if '.' in s:
            base, ext = s.rsplit('.', 1)
            if len(ext) <= 4:
                return f"https://res.cloudinary.com/{cloud_name}/image/upload/{base}.{ext}"
        
        # If no extension found, assume png
        return f"https://res.cloudinary.com/{cloud_name}/image/upload/{s}.png"
        
    except Exception:
        return ''
