# Generated by Django 5.2 on 2025-04-15 13:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_ailments'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('patient', models.CharField(max_length=200)),
                ('ailment', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('specialist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
