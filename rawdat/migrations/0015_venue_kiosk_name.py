# Generated by Django 3.2 on 2021-07-06 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rawdat', '0014_venue_is_focused'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='kiosk_name',
            field=models.CharField(max_length=24, null=True),
        ),
    ]
