# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-26 14:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('developers', '0012_auto_20161026_0252'),
    ]

    operations = [
        migrations.CreateModel(
            name='PullRequestEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=500, unique=True)),
                ('action', models.CharField(max_length=200)),
                ('pr_submitter', models.CharField(max_length=500)),
                ('self_referential', models.BooleanField()),
                ('merged', models.BooleanField()),
                ('action_initiator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='developers.Developer')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='developers.Event', unique=True)),
            ],
        ),
    ]
