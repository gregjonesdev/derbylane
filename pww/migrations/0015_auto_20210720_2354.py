# Generated by Django 3.2 on 2021-07-20 23:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pww', '0014_alter_straightbettype_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='straightbettype',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='straightbettype',
            name='modified_by',
        ),
        migrations.DeleteModel(
            name='Bet',
        ),
        migrations.DeleteModel(
            name='StraightBetType',
        ),
    ]
