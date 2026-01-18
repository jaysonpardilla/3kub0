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

        - If `public_id_or_url` is already a full URL, return it unchanged.
        - If it contains '/image/upload/', assume it's a Cloudinary path and try
          to append the correct extension using the admin API; default to png.
        - Otherwise treat it as a public_id and attempt to detect format via
          `cloudinary.api.resource`. Falls back to `.png` when detection fails.
        """
        try:
            if not public_id_or_url:
                return ''
            s = str(public_id_or_url)
            if s.startswith('http://') or s.startswith('https://'):
                return s

            # Normalize: drop leading slashes
            if s.startswith('/'):
                s = s.lstrip('/')

            # If already contains upload path, take the part after it
            if '/image/upload/' in s:
                public_part = s.split('/image/upload/')[-1]
            else:
                public_part = s

            # If public_part already has an extension, return constructed URL
            if '.' in public_part and len(public_part.rsplit('.', 1)[-1]) <= 4:
                fmt = public_part.rsplit('.', 1)[-1]
                public_id = public_part
            else:
                public_id = public_part
                fmt = None

            # Determine cloud name
            if not cloud_name:
                from django.conf import settings
                cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', '')

            # Try to fetch resource metadata to get the real format
            if not fmt:
                try:
                    import cloudinary.api as _api
                    info = _api.resource(public_id)
                    fmt = info.get('format')
                except Exception:
                    fmt = None

            if fmt:
                return f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}.{fmt}"
            else:
                # Fallback to png extension if unknown
                return f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}.png"
        except Exception:
            return ''
