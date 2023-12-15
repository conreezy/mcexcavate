from django.contrib import admin

# Register your models here.
from .models import Gallery, GalleryImages

class GalleryImagesInline(admin.TabularInline):
    model = GalleryImages

class GalleryImagesAdmin(admin.ModelAdmin):
    list_display = ['alt', 'gallery']
    sortable_by = ('alt')
    search_fields = ['alt']

class GalleryAdmin(admin.ModelAdmin):
    list_display = ['title']
    sortable_by = ('title')
    search_fields = ['title']
    inlines = [
        GalleryImagesInline,
    ]

admin.site.register(GalleryImages, GalleryImagesAdmin)
admin.site.register(Gallery, GalleryAdmin)