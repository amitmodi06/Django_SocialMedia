# Generated by Django 5.0 on 2023-12-13 21:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social_media_app', '0002_posts'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Posts',
            new_name='Post',
        ),
    ]
