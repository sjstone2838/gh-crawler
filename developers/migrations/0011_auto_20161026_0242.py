# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-26 02:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('developers', '0010_repo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repo',
            name='language',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]