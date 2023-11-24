from django.contrib import admin

# Register your models here.
from .models import BlogPost

class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title']
    sortable_by = ('title')
    search_fields = ['title']

admin.site.register(BlogPost, BlogPostAdmin)