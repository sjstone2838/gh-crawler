# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-26 16:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('developers', '0017_auto_20161026_1610'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pullrequest',
            old_name='pr_submitter',
            new_name='opener',
        ),
        migrations.AddField(
            model_name='pullrequest',
            name='closer',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
