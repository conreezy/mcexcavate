import os
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.urls import reverse
from PIL import Image, ImageFile, ImageOps

from .ai_alt_text import generate_alt_text_for_image_file

ImageFile.LOAD_TRUNCATED_IMAGES = True

MAX_GALLERY_IMAGE_DIMENSION = 1600
GALLERY_THUMBNAIL_MAX_SIZE = (240, 180)
JPEG_QUALITY = 85
THUMBNAIL_JPEG_QUALITY = 78
JPEG_SUBSAMPLING = 1


def _should_process_file(instance, field_name, update_fields):
    if update_fields is not None and field_name not in update_fields:
        return False

    file_field = getattr(instance, field_name)
    if not file_field:
        return False

    if not instance.pk:
        return True

    try:
        existing = instance.__class__.objects.only(field_name).get(pk=instance.pk)
    except instance.__class__.DoesNotExist:
        return True

    return getattr(existing, field_name).name != file_field.name


def _normalize_image_mode(image_obj):
    if image_obj.mode in ('RGBA', 'LA'):
        background = Image.new('RGB', image_obj.size, 'WHITE')
        background.paste(image_obj, mask=image_obj.getchannel('A'))
        return background

    if image_obj.mode != 'RGB':
        return image_obj.convert('RGB')

    return image_obj


def _build_processed_upload(uploaded_file, *, max_size, quality, suffix=''):
    uploaded_file.seek(0)
    with Image.open(uploaded_file) as opened_image:
        image_obj = ImageOps.exif_transpose(opened_image)
        image_obj = _normalize_image_mode(image_obj)

        image_obj.thumbnail(max_size, Image.Resampling.LANCZOS)

        output = BytesIO()
        image_obj.save(
            output,
            format='JPEG',
            quality=quality,
            optimize=True,
            progressive=True,
            subsampling=JPEG_SUBSAMPLING,
        )

    output.seek(0)
    base_name = os.path.splitext(os.path.basename(uploaded_file.name))[0]
    file_size = output.getbuffer().nbytes
    return InMemoryUploadedFile(
        output,
        'FileField',
        f'{base_name}{suffix}.jpg',
        'image/jpeg',
        file_size,
        None,
    )


def _optimize_uploaded_image(uploaded_file, *, max_dimension=MAX_GALLERY_IMAGE_DIMENSION, quality=JPEG_QUALITY):
    return _build_processed_upload(
        uploaded_file,
        max_size=(max_dimension, max_dimension),
        quality=quality,
    )


def _build_gallery_thumbnail(uploaded_file, *, max_size=GALLERY_THUMBNAIL_MAX_SIZE, quality=THUMBNAIL_JPEG_QUALITY):
    return _build_processed_upload(
        uploaded_file,
        max_size=max_size,
        quality=quality,
        suffix='_thumb',
    )


class Gallery(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, blank=False, null=True)
    image = models.FileField(upload_to='image/gallery/', blank=False, null=True)
    image_alt = models.CharField(max_length=340, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=False, null=True)
    description = models.TextField(null=True, blank=False)
    meta_title = models.CharField(max_length=55, blank=False, null=True)
    meta_keywords = models.CharField(max_length=160, blank=False, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('gallery:detail', kwargs={'slug': self.slug})

    def get_edit_url(self):
        return reverse('gallery:add_photo', kwargs={'slug': self.slug})

    def get_delete_url(self):
        return reverse('gallery:delete', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        image_changed = _should_process_file(self, 'image', update_fields)

        if image_changed:
            self.image = _optimize_uploaded_image(self.image)
            self.image_alt = generate_alt_text_for_image_file(self.image)

        super().save(*args, **kwargs)


class GalleryImages(models.Model):
    id = models.AutoField(primary_key=True)
    images = models.FileField(upload_to='image/gallery/', blank=True, null=True)
    thumbnail = models.FileField(upload_to='image/gallery/thumbnails/', blank=True, null=True)
    alt = models.CharField(max_length=250, blank=True, null=True)
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        image_changed = _should_process_file(self, 'images', update_fields)

        if image_changed:
            self.images = _optimize_uploaded_image(self.images)
            self.thumbnail = _build_gallery_thumbnail(self.images)
            self.alt = generate_alt_text_for_image_file(self.images)
        elif self.images and not self.thumbnail:
            self.thumbnail = _build_gallery_thumbnail(self.images)

        super().save(*args, **kwargs)
