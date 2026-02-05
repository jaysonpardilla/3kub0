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
    """Return a full Cloudinary URL including an extension when possible.

    This helper is used across templates/model methods.

    - If `public_id_or_url` is already a full URL, return it unchanged (unless malformed).
    - If it contains `/image/upload/`, extract the part after it.
    - Otherwise treat it as a Cloudinary public_id.
    - If no extension is present, try to detect it via `cloudinary.api.resource`.
      Fall back to `.png` when detection fails.
    """
    try:
        if not public_id_or_url:
            return ''

        s = str(public_id_or_url).strip()

        # Handle malformed URLs that contain res.cloudinary.com with embedded URLs
        # Example: https://res.cloudinary.com/.../v123/https:/res.cloudinary.com/.../file.png
        if 'res.cloudinary.com' in s:
            if '/image/upload/' in s:
                # Extract the part after the LAST occurrence of /image/upload/
                # This handles malformed URLs with embedded full URLs
                public_part = s.split('/image/upload/')[-1]
                
                # Clean up any version numbers at the start
                import re
                public_part = re.sub(r'^v\d+/', '', public_part)
                
                # Clean up any remaining URL fragments
                if 'res.cloudinary.com' in public_part:
                    public_part = public_part.split('res.cloudinary.com/')[-1]
                    public_part = re.sub(r'^v\d+/', '', public_part)
                
                # Determine cloud name
                if not cloud_name:
                    from django.conf import settings
                    cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', '')
                
                # If public_part has an extension, use it
                if '.' in public_part and len(public_part.rsplit('.', 1)[-1]) <= 4:
                    base, ext = public_part.rsplit('.', 1)
                    return f"https://res.cloudinary.com/{cloud_name}/image/upload/{base}.{ext}"
                
                # Fallback to png
                return f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_part}.png"
        
        # Already a full URL (normal case) - return unchanged
        if s.startswith('http://') or s.startswith('https://'):
            return s

        # Normalize: drop leading slashes
        s = s.lstrip('/')

        # If already contains upload path, take the part after it
        public_part = s.split('/image/upload/')[-1] if '/image/upload/' in s else s

        # Determine cloud name
        if not cloud_name:
            from django.conf import settings
            cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', '')

        # If public_part already has an extension, split it cleanly
        if '.' in public_part and len(public_part.rsplit('.', 1)[-1]) <= 4:
            base, ext = public_part.rsplit('.', 1)
            return f"https://res.cloudinary.com/{cloud_name}/image/upload/{base}.{ext}"

        # No obvious extension — ask Cloudinary for metadata
        public_id = public_part
        fmt = None
        try:
            import cloudinary.api as _api
            info = _api.resource(public_id)
            fmt = info.get('format')
        except Exception:
            fmt = None

        if fmt:
            return f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}.{fmt}"

        # Fallback to png extension if unknown
        return f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}.png"
    except Exception:
        return ''
