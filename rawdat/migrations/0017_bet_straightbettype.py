# Generated by Django 3.2 on 2021-07-20 23:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rawdat', '0016_alter_venue_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='StraightBetType',
            fields=[
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField()),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(choices=[('P', 'Place'), ('S', 'Show'), ('W', 'Win')], max_length=16)),
                ('cutoff', models.IntegerField()),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rawdat_straightbettype_created_by', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rawdat_straightbettype_modified_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Bet',
            fields=[
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField()),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, default=2.0, max_digits=10)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rawdat_bet_created_by', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rawdat_bet_modified_by', to=settings.AUTH_USER_MODEL)),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rawdat.participant')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rawdat.straightbettype')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]