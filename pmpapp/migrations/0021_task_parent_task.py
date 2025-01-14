# Generated by Django 5.1.2 on 2025-01-10 11:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pmpapp', '0020_alter_project_client_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='parent_task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subtasks', to='pmpapp.task'),
        ),
    ]
