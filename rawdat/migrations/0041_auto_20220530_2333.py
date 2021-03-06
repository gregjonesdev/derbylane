# Generated by Django 3.2 on 2022-05-31 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rawdat', '0040_auto_20220530_2235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sizzle_exacta',
            name='payout',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='sizzle_quinella',
            name='payout',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='sizzle_superfecta',
            name='payout',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='sizzle_trifecta',
            name='payout',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='straight_bet',
            name='payout',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
