# Generated by Django 4.0 on 2022-04-10 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PavingEstimate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('email', models.CharField(blank=True, max_length=100)),
                ('address', models.CharField(blank=True, max_length=100)),
                ('pave_type', models.CharField(blank=True, max_length=100)),
                ('length', models.CharField(blank=True, max_length=100)),
                ('width', models.CharField(blank=True, max_length=100)),
                ('area', models.CharField(blank=True, max_length=100)),
                ('price', models.CharField(blank=True, max_length=100)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]