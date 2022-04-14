from django.contrib import admin

from .models import SodEstimate

class SodEstimateAdmin(admin.ModelAdmin):
    model = SodEstimate

admin.site.register(SodEstimate)