# Generated by Django 3.2 on 2021-05-18 01:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rawdat', '0009_auto_20210514_0508'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dog',
            name='dam',
        ),
        migrations.RemoveField(
            model_name='dog',
            name='kennel',
        ),
        migrations.RemoveField(
            model_name='dog',
            name='last_scanned',
        ),
        migrations.RemoveField(
            model_name='dog',
            name='sire',
        ),
        migrations.RemoveField(
            model_name='dog',
            name='whelp_date',
        ),
    ]
