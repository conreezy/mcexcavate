# Generated by Django 4.1 on 2025-02-17 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0003_alter_gallery_id_alter_galleryimages_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='gallery',
            name='image_alt',
            field=models.CharField(blank=True, max_length=340, null=True),
        ),
    ]
