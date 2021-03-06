# Generated by Django 3.2 on 2022-05-25 06:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rawdat', '0024_alter_quiniela_wager_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exotic_Scan',
            fields=[
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField()),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('start', models.DecimalField(decimal_places=6, max_digits=8, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rawdat_exotic_scan_created_by', to=settings.AUTH_USER_MODEL)),
                ('grade', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='rawdat.grade')),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rawdat_exotic_scan_modified_by', to=settings.AUTH_USER_MODEL)),
                ('venue', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='rawdat.venue')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
