# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-26 17:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('developers', '0019_pullrequest_repo_still_exists'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pullrequest',
            name='closer',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='pullrequest',
            name='merged',
            field=models.NullBooleanField(),
        ),
    ]
