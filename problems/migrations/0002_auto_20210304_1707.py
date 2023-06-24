# Generated by Django 3.1.6 on 2021-03-04 13:07

import core.picture_compressor
from django.db import migrations, models
import problems.models


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='problem',
            old_name='region_kladr',
            new_name='region_iso',
        ),
        migrations.AlterField(
            model_name='category',
            name='icon',
            field=models.ImageField(blank=True, default='categories/default_category_icon.png', null=True, upload_to=problems.models.upload_picture_path, validators=[core.picture_compressor.validate_image], verbose_name='иконка для категории'),
        ),
    ]