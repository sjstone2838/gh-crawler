# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-24 12:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('developers', '0008_temporalpredictor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='temporalpredictor',
            name='period',
        ),
        migrations.AddField(
            model_name='temporalpredictor',
            name='month',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='temporalpredictor',
            name='year',
            field=models.IntegerField(default=2014),
            preserve_default=False,
        ),
    ]
