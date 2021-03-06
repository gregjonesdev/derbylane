# Generated by Django 3.2 on 2021-11-15 04:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rawdat', '0018_alter_participant_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bet_Recommendation',
            fields=[
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField()),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('distance', models.IntegerField()),
                ('prediction', models.IntegerField()),
                ('bet', models.CharField(max_length=16, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rawdat_bet_recommendation_created_by', to=settings.AUTH_USER_MODEL)),
                ('grade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rawdat.grade')),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rawdat_bet_recommendation_modified_by', to=settings.AUTH_USER_MODEL)),
                ('venue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rawdat.venue')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
