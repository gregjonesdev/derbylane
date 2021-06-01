# Generated by Django 3.2 on 2021-05-29 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rawdat', '0011_auto_20210527_2212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='straight_wager',
            name='place',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='straight_wager',
            name='show',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='straight_wager',
            name='win',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, null=True),
        ),
    ]