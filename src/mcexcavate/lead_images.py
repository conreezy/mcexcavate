"""Photo processing shared by form uploads and the worker's size fallback."""
import os
import uuid
import logging

from PIL import Image, ImageOps
from django.conf import settings


MAX_PHOTO_DIMENSION = 1600
PHOTO_JPEG_QUALITY = 80
logger = logging.getLogger(__name__)


def remove_uploaded_files(paths):
    for path in paths:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        except OSError:
            logger.exception('Could not remove a contact photo after a failed submission.')


def save_contact_photo(upload, *, max_dimension=MAX_PHOTO_DIMENSION, quality=PHOTO_JPEG_QUALITY):
    """Decode/resize once and encode one JPEG, retaining no original upload."""
    upload.seek(0)
    with Image.open(upload) as source:
        # Resize before EXIF transposition, avoiding a full-resolution copy.
        # Favor JPEG decoder downsampling to avoid decoding every original pixel.
        source.thumbnail((max_dimension, max_dimension),
                         Image.Resampling.BICUBIC, reducing_gap=1.1)
        photo = ImageOps.exif_transpose(source)
        if photo.mode in ('RGBA', 'LA') or 'transparency' in photo.info:
            rgba = photo.convert('RGBA')
            photo = Image.new('RGB', rgba.size, 'white')
            photo.paste(rgba, mask=rgba.getchannel('A'))
        elif photo.mode != 'RGB':
            photo = photo.convert('RGB')

        upload_dir = os.path.join(settings.MEDIA_ROOT, 'form_uploads')
        os.makedirs(upload_dir, exist_ok=True)
        path = os.path.join(upload_dir, '{}.jpg'.format(uuid.uuid4().hex))
        try:
            # No optimization pass, repeated quality attempts, or EXIF/GPS data.
            photo.save(path, 'JPEG', quality=quality, subsampling=2,
                       optimize=False, progressive=False, exif=b'')
        except Exception:
            remove_uploaded_files([path])
            raise
    return path
