# Generated by Django 3.2 on 2021-06-25 00:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rawdat', '0013_auto_20210531_2258'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='is_focused',
            field=models.BooleanField(default=False),
        ),
    ]
