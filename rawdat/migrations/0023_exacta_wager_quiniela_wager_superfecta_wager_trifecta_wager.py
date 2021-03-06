# Generated by Django 3.2 on 2022-05-12 11:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rawdat', '0022_scannedurl'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trifecta_Wager',
            fields=[
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField()),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, default=2.0, max_digits=10)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rawdat_trifecta_wager_created_by', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rawdat_trifecta_wager_modified_by', to=settings.AUTH_USER_MODEL)),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trifecta_wager_place', to='rawdat.participant')),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trifecta_wager', to='rawdat.race')),
                ('show', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trifecta_wager_show', to='rawdat.participant')),
                ('win', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trifecta_wager_win', to='rawdat.participant')),
            ],
            options={
                'verbose_name': 'Trifecta',
            },
        ),
        migrations.CreateModel(
            name='Superfecta_Wager',
            fields=[
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField()),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, default=2.0, max_digits=10)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rawdat_superfecta_wager_created_by', to=settings.AUTH_USER_MODEL)),
                ('fourth', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='superfecta_wager_fourth', to='rawdat.participant')),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rawdat_superfecta_wager_modified_by', to=settings.AUTH_USER_MODEL)),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='superfecta_wager_place', to='rawdat.participant')),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='superfecta_wager', to='rawdat.race')),
                ('show', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='superfecta_wager_show', to='rawdat.participant')),
                ('win', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='superfecta_wager_win', to='rawdat.participant')),
            ],
            options={
                'verbose_name': 'Trifecta',
            },
        ),
        migrations.CreateModel(
            name='Quiniela_Wager',
            fields=[
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField()),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, default=2.0, max_digits=10)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rawdat_quiniela_wager_created_by', to=settings.AUTH_USER_MODEL)),
                ('left', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quiniela_wager_left', to='rawdat.participant')),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rawdat_quiniela_wager_modified_by', to=settings.AUTH_USER_MODEL)),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quiniela_wager', to='rawdat.race')),
                ('right', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quiniela_wager_right', to='rawdat.participant')),
            ],
            options={
                'verbose_name': 'Quiniela',
            },
        ),
        migrations.CreateModel(
            name='Exacta_Wager',
            fields=[
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField()),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, default=2.0, max_digits=10)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rawdat_exacta_wager_created_by', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rawdat_exacta_wager_modified_by', to=settings.AUTH_USER_MODEL)),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exacta_wager_place', to='rawdat.participant')),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exacta_wager', to='rawdat.race')),
                ('win', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exacta_wager_win', to='rawdat.participant')),
            ],
            options={
                'verbose_name': 'Exacta',
            },
        ),
    ]
