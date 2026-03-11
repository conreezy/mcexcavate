from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField


class BlogPostQuerySet(models.QuerySet):
    def published(self):
        now = timezone.now()
        return self.filter(publish_date__lte=now)


class BlogPostManager(models.Manager):
    def get_queryset(self):
        return BlogPostQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()


Excavation = "Excavation"
ReSodding = "Re-Sodding"
Interlock = "Interlock"
Concrete = "Concrete"
AsphaltPaving = "Asphalt Paving"
AsphaltRepairs = "Asphalt Repairs"

SERVICE_CHOICES = (
    (Excavation, 'Excavation'),
    (ReSodding, 'Re-Sodding'),
    (Interlock, 'Interlock'),
    (Concrete, 'Concrete'),
    (AsphaltPaving, 'Asphalt Paving'),
    (AsphaltRepairs, 'Asphalt Repairs'),
)


class BlogPost(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, default=1, null=True, on_delete=models.SET_NULL)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    image_alt = models.CharField(max_length=340, blank=True, null=True)
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    content = RichTextUploadingField(null=True, blank=True)
    publish_date = models.DateTimeField(default=timezone.now)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    service = models.CharField(max_length=15, choices=SERVICE_CHOICES, default=Excavation)

    objects = BlogPostManager()

    class Meta:
        ordering = ['-publish_date', '-updated', '-timestamp']

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})

    def get_edit_url(self):
        return reverse('blog:edit', kwargs={'slug': self.slug})

    def get_delete_url(self):
        return reverse('blog:delete', kwargs={'slug': self.slug})
