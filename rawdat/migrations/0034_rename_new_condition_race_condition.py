# Generated by Django 3.2 on 2022-05-27 12:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rawdat', '0033_rename_condition_race_legacy_condition'),
    ]

    operations = [
        migrations.RenameField(
            model_name='race',
            old_name='new_condition',
            new_name='condition',
        ),
    ]
