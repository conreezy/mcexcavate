from django.db import models

# Create your models here.
class Gallery(models.Model):
    title   = models.CharField(max_length=50, blank=True, null=True)
    image   = models.FileField(upload_to='image/gallery/', blank=True, null=True)
    slug    = models.SlugField(unique=True, blank=True, null=True) 
    description = models.TextField(null=True, blank=True)
    meta_title  = models.CharField(max_length=55, blank=True, null=True)
    meta_keywords  = models.CharField(max_length=160, blank=True, null=True) 

    def get_absolute_url(self):
        return f"/gallery/{self.slug}"

    def get_edit_url(self):
        return f"{self.get_absolute_url()}/edit"

    def get_delete_url(self):
        return f"{self.get_absolute_url()}/delete"

class GalleryImages(models.Model):
    images = models.FileField(upload_to='image/gallery/', blank=True, null=True)
    alt = models.CharField(max_length=250, blank=True, null=True)
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        alt_text = self.images.url
        alt_text = alt_text.replace('/', '')
        alt_text = alt_text.replace('media', '')
        alt_text = alt_text.replace('image', '')
        alt_text = alt_text.replace('gallery', '')
        alt_text = alt_text.replace('.jpg', '')
        alt_text = alt_text.replace('.JPG', '')
        alt_text = alt_text.replace('.jpeg', '')
        alt_text = alt_text.replace('.JPEG', '')
        alt_text = alt_text.replace('.png', '')
        alt_text = alt_text.replace('.PNG', '')
        self.alt = alt_text

        super(GalleryImages, self).save(*args, **kwargs)