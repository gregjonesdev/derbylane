# Generated by Django 3.2 on 2021-11-09 05:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rawdat', '0017_bet_straightbettype'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='participant',
            options={'ordering': ['post'], 'verbose_name': 'Participant'},
        ),
    ]
