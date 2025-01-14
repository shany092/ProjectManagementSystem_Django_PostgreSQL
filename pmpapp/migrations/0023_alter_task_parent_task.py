# Generated by Django 5.1.2 on 2025-01-10 18:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pmpapp', '0022_alter_project_client_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='parent_task',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(('parent_task__isnull', True)), null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subtasks', to='pmpapp.task'),
        ),
    ]
