from django.contrib import admin

# Register your models here.
from .models import Gallery, GalleryImages

class GalleryImagesInline(admin.TabularInline):
    model = GalleryImages

class GalleryAdmin(admin.ModelAdmin):
    inlines = [
        GalleryImagesInline,
    ]

admin.site.register(GalleryImages)
admin.site.register(Gallery)