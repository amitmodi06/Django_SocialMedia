# Generated by Django 5.0 on 2023-12-26 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_media_app', '0004_likepost'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='profilebanner',
            field=models.ImageField(default='df-banner-placeholder.png', upload_to='profile_banner'),
        ),
    ]