"""Conservative checks for captured visuals with no visible image content."""
import base64
import io


def empty_visual(image, *, decoded=None):
    """Reject fully transparent images and exact solid black/white captures.

    Exact pixel checks deliberately leave low-contrast photographs, minimal
    white layouts and uncertain/unsupported image formats alone.
    """
    data = image.get('data') if isinstance(image, dict) else None
    if not isinstance(data, str) or not data.startswith('data:image/') or ',' not in data:
        return False
    try:
        from PIL import Image
        if decoded is not None:
            channels = decoded.convert('RGBA').getextrema()
        else:
            with Image.open(io.BytesIO(base64.b64decode(data.split(',', 1)[1]))) as im:
                channels = im.convert('RGBA').getextrema()
        red, green, blue, alpha = channels
        if alpha[1] == 0:
            return True
        if alpha == (255, 255) and red == green == blue and red in ((0, 0), (255, 255)):
            return True
    except Exception:
        return False
    return False
