# Generated by Django 4.0 on 2022-04-10 21:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='SodEstimate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('email', models.CharField(blank=True, max_length=100)),
                ('address', models.CharField(blank=True, max_length=100)),
                ('yard', models.CharField(blank=True, max_length=100)),
                ('length', models.FloatField(blank=True, max_length=100)),
                ('width', models.FloatField(blank=True, max_length=100)),
                ('area', models.FloatField(blank=True, max_length=100)),
                ('price', models.FloatField(blank=True, max_length=100, null=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField(blank=True, max_length=100)),
                ('hst', models.FloatField(blank=True, max_length=100)),
                ('total_price', models.FloatField(blank=True, max_length=100)),
                ('deposit', models.FloatField(blank=True, max_length=100)),
                ('payment1', models.FloatField(blank=True, max_length=100)),
                ('payment2', models.FloatField(blank=True, max_length=100)),
                ('payment3', models.FloatField(blank=True, max_length=100)),
                ('payment4', models.FloatField(blank=True, max_length=100)),
                ('discount', models.FloatField(blank=True, max_length=100)),
                ('balance', models.FloatField(blank=True, max_length=100)),
                ('user', models.ForeignKey(blank=True, max_length=10000, null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
        ),
    ]
