# Generated by Django 3.2 on 2022-05-31 03:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rawdat', '0039_delete_exotic_bet_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exotic_scan',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='exotic_scan',
            name='grade',
        ),
        migrations.RemoveField(
            model_name='exotic_scan',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='exotic_scan',
            name='venue',
        ),
        migrations.RemoveField(
            model_name='race',
            name='legacy_condition',
        ),
        migrations.RemoveField(
            model_name='race',
            name='legacy_grade',
        ),
        migrations.DeleteModel(
            name='Bet_Recommendation',
        ),
        migrations.DeleteModel(
            name='Exotic_Scan',
        ),
    ]
