# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-26 02:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('developers', '0011_auto_20161026_0242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repo',
            name='homepage',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]