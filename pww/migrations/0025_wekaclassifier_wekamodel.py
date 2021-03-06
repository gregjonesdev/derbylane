# Generated by Django 3.2 on 2022-05-26 02:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pww', '0024_auto_20220525_0126'),
    ]

    operations = [
        migrations.CreateModel(
            name='WekaClassifier',
            fields=[
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField()),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('is_nominal', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pww_wekaclassifier_created_by', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pww_wekaclassifier_modified_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WekaModel',
            fields=[
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField()),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('training_start', models.DateField()),
                ('training_end', models.DateField()),
                ('betting_grade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pww.bettinggrade')),
                ('classifier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pww.wekaclassifier')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pww_wekamodel_created_by', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pww_wekamodel_modified_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
