# Generated by Django 3.2 on 2022-05-30 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pww', '0027_auto_20220528_0243'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant_prediction',
            name='smoreg',
            field=models.DecimalField(decimal_places=8, max_digits=16, null=True),
        ),
    ]
