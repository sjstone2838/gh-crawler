# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-26 15:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('developers', '0014_auto_20161026_1500'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PullRequestEvent',
            new_name='PullRequest',
        ),
    ]
